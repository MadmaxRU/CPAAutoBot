
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

def write_to_gsheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("CPA Auto Leads").sheet1
    sheet.append_row([data.get("name", ""), data.get("city", ""), data.get("brand", ""), data.get("payment", ""), data.get("region", ""), data.get("agreement", "")])
