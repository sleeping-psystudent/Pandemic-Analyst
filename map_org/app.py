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
    for original, new_title in title_map.items():
        cleaned_text = cleaned_text.replace(original, new_title)
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
    return "<br>".join(formatted_sections)

# 設定頁面
st.set_page_config(page_title="國際疫情地圖", layout="wide")

# 注入自定義 CSS 固定地圖位置
st.markdown(
    """
    <style>
    /* 固定地圖容器 */
    .map-container {
        position: fixed;
        height: 100%;
        left: 0px; /* 側邊欄的寬度 */
        margin: 0px;
        padding: 0px;
        z-index: 2000;
    }

    .st-emotion-cache-1jicfl2 {
        position: fixed;
        height: 100%;
        width: 100%;
        padding: 0rem 0rem 0rem;
    }

    .st-emotion-cache-0.e1f1d6gn0 {
    height: 95vh;
    }
    .st-emotion-cache-1wmy9hl.e1f1d6gn1 {
        height: 95vh;
    }
    .st-emotion-cache-0.elp1w7k0 {
        height: 95vh;
    }
    
    .stDeckGlJsonChart {
        height: 95vh !important; /* 將高度設置為視窗高度 */
    }
    
    #deckgl-wrapper {
        box-sizing: content-box !important;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 95 !important;
        z-index: 10000;
    }

    .st-emotion-cache-bm2z3a {
        height: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 連接資料庫與讀取資料
conn = sqlite3.connect('./map_org/disease_info.db')  
cursor = conn.cursor()
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
today = datetime.now()
map_data['weeks_ago'] = map_data['date'].apply(lambda x: (today - datetime.strptime(x, '%Y-%m-%d')).days // 7)
map_data['color'] = map_data.apply(lambda x: risk_colors[x['risk_assessment']][1] + [150], axis=1)
map_data['radius'] = map_data['risk_assessment'].apply(lambda x: risk_colors[x][2])

layer = pdk.Layer(
    'ScatterplotLayer',
    data=map_data,
    get_position='[lon, lat]',
    get_radius='radius',
    get_fill_color='color',
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(latitude=25.09108, longitude=121.5598, zoom=3, pitch=0)
# view_state = pdk.ViewState(height = 800, latitude=20, longitude=0, zoom=1, pitch=0)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "style":{
            "font-size": "12px",
            "opacity": 0.9,
            "overflow": "scroll",
            "z-index": 2147483647
        },
        "html": """
            <div class='tooltip' style="
            max-width: 400px;">
                <h5>{emoji} {risk_assessment}</h5>
                 <small style="font-size: 10px;">|| 發布日期: {date} ({weeks_ago} 週前)</small><hr>
                <div>{summary}</div>
            </div>
        """
    }
)

# 顯示固定地圖
st.markdown('<div class="map-container">', unsafe_allow_html=True)
st.pydeck_chart(r , height=700)
st.markdown('</div>', unsafe_allow_html=True)


# with st.expander("疫情資料表"):
#     st.write("#### 📊 疫情資料表")

#     # 建立四個篩選器
#     col1, col2, col3, col4 = st.columns(4)

#     with col1:
#         selected_risks = selected_country = st.selectbox(
#             "Risk Assessment", 
#             options=["All"] + list(map_data['risk_assessment'].unique())
#         )

#     with col2:
#         selected_weeks = st.selectbox(
#             "How long ago", 
#             options=["All"] + list(map_data['weeks_ago'].unique())
#         )

#     with col3:
#         selected_country = st.selectbox(
#             "Country", 
#             options=["All"] + list(map_data['country'].unique())
#         )

#     with col4:
#         selected_disease = st.selectbox(
#             "Disease", 
#             options=["All"] + list(map_data['disease_name'].unique())
#         )

#     # 根據使用者選擇進行資料篩選
#     filtered_data = map_data[
#         ((map_data['risk_assessment'] == selected_risks) | (selected_risks == "All")) &
#         ((map_data['weeks_ago'] == selected_weeks) | (selected_weeks == "All")) &
#         ((map_data['country'] == selected_country) | (selected_country == "All")) &
#         ((map_data['disease_name'] == selected_disease) | (selected_disease == "All")) 
#     ]

#     # 顯示篩選後的資料表
#     st.data_editor(
#         filtered_data[['emoji', 'weeks_ago', 'date', 'country', 'disease_name']],
#         column_config={
#             'weeks_ago': "Weeks Ago",
#             'date': "Date",
#             'emoji': "Risk",
#             'country': "Country",
#             'disease_name': "Disease"
#         },
#         hide_index=True,
#         use_container_width=True,
#         key="data_editor"
#     )

# https://github.com/streamlit/streamlit/issues/1043
# https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart
