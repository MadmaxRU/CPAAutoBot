import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def write_to_gsheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(os.getenv("SPREADSHEET_ID"))
    worksheet = spreadsheet.sheet1

    worksheet.append_row([
        data.get("lead_type", ""),
        data.get("city", ""),
        data.get("car_brand", ""),
        data.get("year", ""),
        data.get("payment_method", ""),
        data.get("name", ""),
        data.get("phone", ""),
        data.get("from_abroad", ""),
        data.get("agreement", "")
    ])
