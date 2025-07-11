import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

def write_to_gsheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = eval(os.getenv("GOOGLE_CREDS_JSON"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1

    row = [
        data.get("method", ""),
        data.get("company_type", ""),
        data.get("inn", ""),
        data.get("email", ""),
        data.get("brand", ""),
        data.get("budget", ""),
        data.get("city", ""),
        data.get("contact", ""),
        data.get("comment", "")
    ]
    sheet.append_row(row)
