
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(os.getenv("SHEET_ID")).worksheet("Sheet1")

def save_to_sheet(data):
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        data.get("payment", ""),
        data.get("brand", ""),
        data.get("company_name", ""),
        data.get("email", ""),
        f"{data.get('name', '')} | {data.get('phone', '')}",
        data.get("budget", ""),
        data.get("city", ""),
        data.get("comment", "")
    ]
    sheet.append_row(row)
