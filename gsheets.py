import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# Подключение к таблице
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1  # Лист по умолчанию

def write_to_gsheet(data):
    print("🚀 Передача данных в таблицу:", data)  # Лог для отладки
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
