# test_access.py

from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1J8WJobKJSeDEybF7rdDAB6hoFQCyeKsd8TcgOsMCIlo'
SHEET_NAME = 'theater_test'  # Adjust based on actual sheet name

try:
    print("Loading credentials from credentials.json...")
    creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    print("Credentials loaded successfully.")
    print(f"Service account email: {creds.service_account_email}")
    service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
    print("Google Sheets service built successfully.")
    sheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID, ranges=[SHEET_NAME], includeGridData=True).execute()
    print("Successfully accessed the spreadsheet.")
    print(sheet.get('properties', {}).get('title'))
except Exception as e:
    print(f"Error: {e}")