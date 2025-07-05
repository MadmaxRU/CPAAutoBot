import gspread
from oauth2client.service_account import ServiceAccountCredentials

def write_to_gsheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("CPA Leads").sheet1
    sheet.append_row([
        data["lead_type"], data["name"], data["city"], data["car_brand"],
        data["payment_method"], data["phone"], data["from_abroad"], data["agreement"]
    ])
