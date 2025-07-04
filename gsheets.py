import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1

def write_to_gsheet(data):
    print("🚀 Передача данных в таблицу:", data)
    sheet.append_row([
        data.get("lead_type", ""),
        data.get("legal_type", ""),
        data.get("inn", ""),
        data.get("email", ""),
        data.get("car_brand", ""),
        data.get("budget", ""),
        data.get("city", ""),
        data.get("name", ""),
        data.get("phone", ""),
        data.get("comment", "")
    ])
