
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

GOOGLE_CREDS_JSON = 'YOUR_CREDENTIALS_JSON'
SHEET_ID = 'YOUR_SHEET_ID'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_dict = json.loads(GOOGLE_CREDS_JSON)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID).sheet1

def save_to_sheet(data):
    sheet.append_row([
        data.get("name", ""),
        data.get("phone", ""),
        data.get("region", "")
    ])
