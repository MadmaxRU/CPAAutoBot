import gspread
import os
import json
from google.oauth2.service_account import Credentials

def write_to_gsheet(data):
    creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
    creds = Credentials.from_service_account_info(creds_dict)
    gc = gspread.authorize(creds)
    sheet = gc.open("CPAauto_leads").sheet1
    row = [
        data.get("lead_type", ""),
        data.get("name", ""),
        data.get("city", ""),
        data.get("car_brand", ""),
        data.get("payment_method", ""),
        data.get("from_abroad", ""),
        data.get("agreement", ""),
        data.get("phone", "")
    ]
    sheet.append_row(row)
