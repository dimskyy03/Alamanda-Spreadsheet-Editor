# main.py
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from theater_show import display_theater_content, append_theater_row, theater_form
from video_call import display_video_call_content, append_video_call_row, video_call_form
from utils import apply_row_formatting, get_sheet_id

# Function to connect to Google Sheets API
def connect_to_gsheet():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    try:
        creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets API: {e}")
        return None

# Main Streamlit app function
def main():
    st.title("Google Sheet Inspector and Row Adder")

    # Sidebar for sheet selection
    sheet_options = ["theater_test", "VC 2025_test"]
    selected_sheet = st.sidebar.selectbox("Select Sheet", sheet_options)
    st.write(f"Selected Sheet: {selected_sheet}")

    # Connect to the Google Sheet
    service = connect_to_gsheet()
    if not service:
        return

    spreadsheet_id = "1J8WJobKJSeDEybF7rdDAB6hoFQCyeKsd8TcgOsMCIlo"
    sheet_title = selected_sheet

    # Initialize event_colors in session state if not present
    if "event_colors" not in st.session_state:
        st.session_state.event_colors = {}

    # Display sheet content and handle row addition based on selected sheet
    if selected_sheet == "theater_test":
        headers, data, month_sections, total_rows = display_theater_content(service, spreadsheet_id, sheet_title)
        if headers:
            theater_form(service, spreadsheet_id, sheet_title, headers, data, month_sections, total_rows)
    else:  # Video Call
        headers, data, month_sections, total_rows = display_video_call_content(service, spreadsheet_id, sheet_title)
        if headers:
            video_call_form(service, spreadsheet_id, sheet_title, headers, data, month_sections, total_rows)

if __name__ == "__main__":
    main()