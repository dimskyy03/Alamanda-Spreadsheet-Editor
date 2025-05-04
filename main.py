# main.py
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from theater_show import display_theater_content, append_theater_row, theater_form
from video_call import display_video_call_content, append_video_call_row, video_call_form
from utils import apply_row_formatting, get_sheet_id
import logging

logging.basicConfig(level=logging.DEBUG)

# Function to connect to Google Sheets API
# Function to connect to Google Sheets API
def connect_to_gsheet():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    try:
        # Access credentials from secrets.toml
        st.write("Loading credentials from secrets.toml...")
        creds_dict = {
            "type": st.secrets["gcp_service_account"]["type"],
            "project_id": st.secrets["gcp_service_account"]["project_id"],
            "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
            "private_key": st.secrets["gcp_service_account"]["private_key"],
            "client_email": st.secrets["gcp_service_account"]["client_email"],
            "client_id": st.secrets["gcp_service_account"]["client_id"],
            "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
            "token_uri": st.secrets["gcp_service_account"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
        }
        
        # Create credentials object from the dictionary
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        st.write("Credentials loaded successfully.")
        st.write(f"Service account email: {creds.service_account_email}")
        # Build service with cache disabled
        service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
        st.write("Google Sheets service built successfully.")
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