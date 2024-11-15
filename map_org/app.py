import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pydeck as pdk

# 格式化文章文字
def format_text(text):
    title_map = {
        "新聞摘要": "📰 <strong>新聞摘要</strong>",
        "特殊情況": "⚕️ <strong>特殊情況</strong>"
    }
    
    cleaned_text = text.replace("*", "").replace("#", "").strip()

    # 替換標題
    for original, new_title in title_map.items():
        cleaned_text = cleaned_text.replace(original, new_title)

    # 處理列點符號 (- 轉換為 1., 2., ...)
    def replace_bullet_points(text_block):
        lines = text_block.splitlines()
        formatted_lines = []
        counter = 1
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("-"):
                formatted_line = f"{counter}. {stripped_line[1:].strip()}"
                counter += 1
            else:
                formatted_line = stripped_line
            formatted_lines.append(formatted_line)
        return "<br>".join(formatted_lines)

    sections = cleaned_text.split("\n\n")  
    formatted_sections = [replace_bullet_points(section) for section in sections]

    return "<br><br>".join(formatted_sections)

# 設定頁面
st.set_page_config(page_title="國際疫情地圖", layout="wide")

# 連接資料庫
conn = sqlite3.connect('./map_org/disease_info.db')  
cursor = conn.cursor()

# 讀取資料表
df = pd.read_sql_query("SELECT * FROM disease_info", conn)

# 風險顏色與 emoji 對應
risk_colors = {
    'High Concern': ('🔴', [255, 0, 0], 150000),
    'Medium Concern': ('🟠', [255, 165, 0], 100000),
    'Low Concern': ('🟡', [255, 255, 0], 50000),
    'Watchlist Alert': ('🟢', [0, 255, 0], 30000)
}

st.sidebar.header("全球疫情地圖")
st.sidebar.markdown("#### 📊 風險等級說明", unsafe_allow_html=True)
for risk, (emoji, color, _) in risk_colors.items():
    st.sidebar.markdown(f"{emoji} {risk}", unsafe_allow_html=True)

# 日期篩選
weeks_range = st.sidebar.slider("#### 🗓️ 顯示距今的週範圍", 1, 52, (4, 10))
start_date = datetime.now() - timedelta(weeks=weeks_range[1])
end_date = datetime.now() - timedelta(weeks=weeks_range[0])

# 處理日期欄位
df['date'] = pd.to_datetime(df['date'], format='%b %d, %Y')
filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# 選擇疾病種類
selected_disease = st.sidebar.selectbox("#### 🦠 選擇疾病種類", options=["All"] + list(filtered_df['disease_name'].unique()))
filtered_df = filtered_df[(filtered_df['disease_name'] == selected_disease) | (selected_disease == "All")]

# 選擇風險等級
risk_options = list(risk_colors.keys())
selected_risks = st.sidebar.multiselect("#### 🚨 選擇風險等級", risk_options, default=risk_options)
filtered_df = filtered_df[filtered_df['risk_assessment'].isin(selected_risks)]

# 處理 location 欄位
location_data = []
for _, row in filtered_df.iterrows():
    locations = row['location'].split('\n')
    for loc in locations:
        lat_lon = loc.split(',')
        if len(lat_lon) == 2:
            try:
                lat = float(lat_lon[0].strip())
                lon = float(lat_lon[1].strip())
                location_data.append({
                    'country': row['country'],
                    'disease_name': row['disease_name'],
                    'lat': lat,
                    'lon': lon,
                    'risk_assessment': row['risk_assessment'],
                    'emoji': risk_colors[row['risk_assessment']][0],
                    'summary': format_text(row['summary']),
                    'date': datetime.strftime(row['date'], '%Y-%m-%d')
                })
            except ValueError:
                continue

map_data = pd.DataFrame(location_data)

# 計算日期距今週數
today = datetime.now()
map_data['weeks_ago'] = map_data['date'].apply(lambda x: (today - datetime.strptime(x, '%Y-%m-%d')).days // 7)

# 設定地圖層
map_data['color'] = map_data.apply(
    lambda x: risk_colors[x['risk_assessment']][1] + [150], axis=1
)
map_data['radius'] = map_data['risk_assessment'].apply(
    lambda x: risk_colors[x][2]
)

layer = pdk.Layer(
    'ScatterplotLayer',
    data=map_data,
    get_position='[lon, lat]',
    get_radius='radius',
    get_fill_color='color',
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1, pitch=0)

# 地圖互動
tooltip_style = """
    <style>
    .tooltip {
        padding: 12px; /* 內距 */
        color: white; /* 文字顏色為白色 */
    }

    .tooltip small {
        float: left;
        color: gray;
    }
    </style>
"""
st.markdown(tooltip_style, unsafe_allow_html=True)


r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": """
            <div class='tooltip' style="
            max-width: 600px;">
                <h4>{emoji} {risk_assessment}</h4>
                <small>|| 發布日期: {date} ({weeks_ago} 週前)</small><hr>
                <div>{summary}</div>
            </div>
        """
    }
)

# 使用 container 將地圖與表格區隔開
with st.container():
    st.pydeck_chart(r, use_container_width=True)  # 顯示地圖

with st.expander("疫情資料表"):
    st.write("#### 📊 疫情資料表")

    # 建立四個篩選器
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_risks = selected_country = st.selectbox(
            "Risk Assessment", 
            options=["All"] + list(map_data['risk_assessment'].unique())
        )

    with col2:
        selected_weeks = st.selectbox(
            "How long ago", 
            options=["All"] + list(map_data['weeks_ago'].unique())
        )

    with col3:
        selected_country = st.selectbox(
            "Country", 
            options=["All"] + list(map_data['country'].unique())
        )

    with col4:
        selected_disease = st.selectbox(
            "Disease", 
            options=["All"] + list(map_data['disease_name'].unique())
        )

    # 根據使用者選擇進行資料篩選
    filtered_data = map_data[
        ((map_data['risk_assessment'] == selected_risks) | (selected_risks == "All")) &
        ((map_data['weeks_ago'] == selected_weeks) | (selected_weeks == "All")) &
        ((map_data['country'] == selected_country) | (selected_country == "All")) &
        ((map_data['disease_name'] == selected_disease) | (selected_disease == "All")) 
    ]

    # 顯示篩選後的資料表
    st.data_editor(
        filtered_data[['emoji', 'weeks_ago', 'date', 'country', 'disease_name']],
        column_config={
            'weeks_ago': "Weeks Ago",
            'date': "Date",
            'emoji': "Risk",
            'country': "Country",
            'disease_name': "Disease"
        },
        hide_index=True,
        use_container_width=True,
        key="data_editor"
    )
