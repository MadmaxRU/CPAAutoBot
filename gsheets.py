import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("CPAauto").sheet1

def write_to_sheet(data):
    row = [data["user_id"], data["username"], data["text"]]
    sheet.append_row(row)
