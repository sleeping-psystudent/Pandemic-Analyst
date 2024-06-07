import openpyxl
from openpyxl import Workbook
import os

def write_to_excel(file_path, data):
    file_exists = os.path.exists(file_path)

    if file_exists:
        # 如果檔案存在，則打開檔案並接續寫入
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
    else:
        # 如果檔案不存在，則新建檔案
        workbook = Workbook()
        sheet = workbook.active
        # 寫入標題行
        sheet.append(["title", "summary", "風險評估", "診斷方式", "病原體種類", "宿主類型", "基本傳染數", "傳播方式", "死亡率", "有無治療方式", "有無疫苗", "GDP", "人口密度", "穩定程度"])
        
    sheet.append(data)
    workbook.save(file_path)