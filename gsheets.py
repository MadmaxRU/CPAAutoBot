import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

# Подключение к Google Sheets через credentials.json
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

with open("/etc/secrets/credentials.json") as f:
    creds_dict = json.load(f)

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Получаем таблицу по SHEET_ID из переменной окружения
sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1

def write_to_gsheet(data):
    print("🚀 Передача данных в таблицу:", data)
    sheet.append_row([
        data.get("lead_type", ""),
        data.get("city", ""),
        data.get("car_brand", ""),
        data.get("payment_method", ""),
        data.get("name", ""),
        data.get("phone", ""),
        data.get("from_abroad", ""),
        data.get("agreement", "")
    ])
