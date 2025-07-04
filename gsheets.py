import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1
with open("/etc/secrets/credentials.json") as f:
    creds_dict = json.load(f)
def write_to_gsheet(data):
    print("🚀 Передача данных в таблицу:", data)
    sheet.append_row([
        data.get("car_brand", ""),
        data.get("year", ""),
        data.get("city", ""),
        data.get("payment_method", ""),
        data.get("name", ""),
        data.get("phone", ""),
        data.get("from_abroad", ""),
        data.get("agreement", "")
    ])
