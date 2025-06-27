import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Подключение к Google Sheets через credentials.json, загруженный как Secret File
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "/etc/secrets/credentials.json", scope
)
client = gspread.authorize(creds)

# Подключаемся к таблице по ключу из переменной среды
sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1  # Первый лист

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
