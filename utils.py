# utils.py
import re
from googleapiclient.errors import HttpError

# Function to convert column index to letter (e.g., 0 -> A, 1 -> B)
def col_index_to_letter(index):
    letter = ''
    while index >= 0:
        letter = chr(65 + (index % 26)) + letter
        index = (index // 26) - 1
    return letter

# Function to validate date format (DD/MM/YYYY)
def validate_date(tanggal):
    pattern = r"^\d{2}/\d{2}/\d{4}$"
    if not re.match(pattern, tanggal):
        return False
    try:
        day, month, year = map(int, tanggal.split('/'))
        if not (1 <= day <= 31 and 1 <= month <= 12 and 2000 <= year <= 9999):
            return False
        return True
    except ValueError:
        return False

# Function to apply formatting to a row
def apply_row_formatting(service, spreadsheet_id, sheet_id, row_index, is_header=False, is_title=False, sheet_name="Theater1"):
    try:
        # Determine the background color based on the row type
        if is_title:
            background_color = {
                "red": 1.0,
                "green": 0.4,
                "blue": 0.8
            }  # Pink for title row in "Video Call"
        elif is_header:
            background_color = {
                "red": 0.8,
                "green": 0.0,
                "blue": 0.8
            }  # Purple for headers
        else:
            background_color = {
                "red": 0.0,
                "green": 1.0,
                "blue": 1.0
            }  # Cyan for month rows in "Theater1"

        end_column = 5 if sheet_name == "theater_test" else 4  # 5 columns for Theater1, 4 for Video Call

        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row_index - 1,  # 0-based index
                        "endRowIndex": row_index,
                        "startColumnIndex": 0,
                        "endColumnIndex": end_column
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": background_color,
                            "horizontalAlignment": "CENTER",
                            "textFormat": {
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat.bold)"
                }
            }
        ]

        body = {"requests": requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
    except HttpError as e:
        print(f"Error applying formatting: {e}")

# Function to get the sheet ID (required for formatting)
def get_sheet_id(service, spreadsheet_id, sheet_title):
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in spreadsheet['sheets']:
            if sheet['properties']['title'] == sheet_title:
                return sheet['properties']['sheetId']
        return None
    except HttpError as e:
        print(f"Error fetching sheet ID: {e}")
        return None