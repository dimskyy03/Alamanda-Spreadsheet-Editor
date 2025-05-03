# video_call.py
import streamlit as st
from googleapiclient.errors import HttpError
from datetime import datetime
from utils import validate_date, apply_row_formatting, get_sheet_id

# Dictionary for month names in Bahasa Indonesia
MONTH_NAMES_ID = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember"
}

# Function to format date as "date, month year" with month in Bahasa Indonesia
def format_date_indonesian(tanggal):
    try:
        day, month, year = map(int, tanggal.split('/'))
        month_name = MONTH_NAMES_ID[month]
        return f"{day}, {month_name} {year}"
    except:
        return tanggal  # Fallback to original format if parsing fails

# Function to convert hex color to RGB (for Google Sheets API)
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return {
        "red": int(hex_color[0:2], 16) / 255.0,
        "green": int(hex_color[2:4], 16) / 255.0,
        "blue": int(hex_color[4:6], 16) / 255.0
    }

# Function to apply background color to a row based on Nama Event
def apply_event_color(service, spreadsheet_id, sheet_id, row_index, event_name, event_colors):
    try:
        color = event_colors.get(event_name, "#FFFFFF")  # Default to white if no color is set
        rgb_color = hex_to_rgb(color)
        
        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row_index - 1,  # 0-based index
                        "endRowIndex": row_index,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4  # Columns A to D
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": rgb_color
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            }
        ]

        body = {"requests": requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
    except HttpError as e:
        st.error(f"Error applying event color: {e}")

# Function to display sheet content for Video Call
def display_video_call_content(service, spreadsheet_id, sheet_title):
    try:
        sheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=[sheet_title],
            includeGridData=True
        ).execute()
        sheet_data = sheet['sheets'][0]
        grid_data = sheet_data.get('data', [{}])[0].get('rowData', [])
    except HttpError as e:
        st.error(f"Error fetching sheet data: {e}")
        return None, None, None, None

    # Extract title rows, headers, and data
    title_row_1 = []
    headers = []
    data = []

    if len(grid_data) >= 1:
        title_row_1 = [cell.get('formattedValue', '') for cell in grid_data[1].get('values', [])]
    if len(grid_data) >= 2:
        headers = [cell.get('formattedValue', '') for cell in grid_data[2].get('values', [])]

    expected_headers = ['Sesi', 'Waktu', 'Tanggal', 'Nama Event']
    if not headers:
        st.error("No headers found in the sheet (Row 2).")
        return None, None, None, None

    if headers != expected_headers:
        st.error(f"Header mismatch. Found: {headers}, Expected: {expected_headers}")
        return None, None, None, None

    # Parse data
    for row in grid_data[2:]:
        row_values = [cell.get('formattedValue', '') for cell in row.get('values', [])]
        while len(row_values) < len(headers):
            row_values.append('')
        if any(val for val in row_values):  # Exclude empty rows
            data.append(row_values)

    return headers, data, None, len(grid_data)

# Function to append new row for Video Call
def append_video_call_row(service, spreadsheet_id, sheet_title, headers, data, month_sections, total_rows, new_row_data, apply_row_formatting, get_sheet_id):
    try:
        sesi, waktu, tanggal, nama_event, event_color = new_row_data
        # Format the date to "date, month year" with month in Bahasa Indonesia
        formatted_date = format_date_indonesian(tanggal)
        last_row_idx = total_rows
        range_str = f"{sheet_title}!A{last_row_idx + 1}"
        new_row = [sesi, waktu, formatted_date, nama_event]

        # Append the new row
        st.write(f"Attempting to append row to: {range_str}")
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_str,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [new_row]}
        ).execute()

        # Update event_colors in session state
        if "event_colors" not in st.session_state:
            st.session_state.event_colors = {}
        st.session_state.event_colors[nama_event] = event_color

        # Apply the color to the row
        sheet_id = get_sheet_id(service, spreadsheet_id, sheet_title)
        if sheet_id is not None:
            apply_event_color(service, spreadsheet_id, sheet_id, last_row_idx + 1, nama_event, st.session_state.event_colors)

        return True
    except HttpError as e:
        st.error(f"HTTP Error appending row: {e}")
        st.error(f"Error details: {e.content.decode('utf-8') if e.content else 'No additional details'}")
        return False
    except Exception as e:
        st.error(f"General error appending row: {e}")
        return False

# Function to render the input form for Video Call
def video_call_form(service, spreadsheet_id, sheet_title, headers, data, month_sections, total_rows):
    st.subheader(f"Add New Row to {sheet_title}")
    
    # Initialize event_colors in session state if not present
    if "event_colors" not in st.session_state:
        st.session_state.event_colors = {}

    with st.form("add_row_form"):
        sesi = st.selectbox("Sesi", options=["sesi 1", "sesi 2", "sesi 3", "sesi 4", "sesi 5", "sesi 6"], help="Select the session")
        waktu = st.selectbox("Waktu", options=[
            "11:15 WIB - 12:15 WIB",
            "13:15 WIB - 14:15 WIB",
            "14:45 WIB - 15:45 WIB",
            "16:30 WIB - 17:30 WIB",
            "18:00 WIB - 19:00 WIB",
            "19:30 WIB - 20:30 WIB"
        ], help="Select the time slot")
        tanggal = st.date_input("Tanggal", help="Date in DD/MM/YYYY format")
        if isinstance(tanggal, str):
            tanggal = tanggal.strftime("%d/%m/%Y")
        else:
            tanggal = tanggal.strftime("%d/%m/%Y")
        nama_event = st.text_input("Nama Event", help="Name of the event")
        
        # Color picker for the event
        default_color = st.session_state.event_colors.get(nama_event, "#FFFFFF")  # Default to white if no color is set
        event_color = st.color_picker("Select color for this event", value=default_color, help="Choose a color for this event")

        new_row_data = (sesi, waktu, tanggal, nama_event, event_color)

        if st.form_submit_button("Submit"):
            if sesi and waktu and tanggal and nama_event:
                if not validate_date(tanggal):
                    st.error("Tanggal must be in DD/MM/YYYY format with valid date.")
                else:
                    if append_video_call_row(service, spreadsheet_id, sheet_title, headers, data, month_sections, total_rows, new_row_data, apply_row_formatting, get_sheet_id):
                        st.success(f"Successfully added new row for {sesi} on {format_date_indonesian(tanggal)}.")
            else:
                st.warning("Please fill in all fields.")