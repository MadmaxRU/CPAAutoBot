
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# Подключение к Google Sheets через сервисный аккаунт
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# Открываем таблицу
sheet = client.open("CPAauto_leads").sheet1

def write_to_sheet(data):
    try:
        sheet.append_row([
            data.get("city", ""),
            data.get("brand", ""),
            data.get("payment_method", ""),
            data.get("year", ""),
            data.get("budget", ""),
            data.get("imported", ""),
            data.get("name", ""),
            data.get("phone", "")
        ])
    except Exception as e:
        print("Ошибка записи в таблицу:", e)
