# test_auth.py
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1J8WJobKJSeDEybF7rdDAB6hoFQCyeKsd8TcgOsMCIlo'

try:
    creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    print("Credentials loaded successfully.")
    print(f"Service account email: {creds.service_account_email}")
    service = build('sheets', 'v4', credentials=creds)
    print("Google Sheets service built successfully.")
    sheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    print("Successfully accessed the spreadsheet.")
    print(sheet.get('properties', {}).get('title'))
except Exception as e:
    print(f"Error: {e}")