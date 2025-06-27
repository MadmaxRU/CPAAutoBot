import gspread
from oauth2client.service_account import ServiceAccountCredentials

def write_to_sheet(name, brand, model, color, phone):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("CPAauto_leads").sheet1
    sheet.append_row([name, brand, model, color, phone])
