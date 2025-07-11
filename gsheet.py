import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

def write_to_gsheet(data):
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes)
    client = gspread.authorize(credentials)
    sheet = client.open("CPAauto").worksheet("Лист1")
    sheet.append_row([
        data.get("deal_type", ""),
        data.get("car_brand", ""),
        data.get("budget", ""),
        data.get("contact", ""),
        data.get("comment", "")
    ])
