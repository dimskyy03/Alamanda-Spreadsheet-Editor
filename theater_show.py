# theater.py
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

# Function to extract month name and year from date string in Bahasa Indonesia
def get_month_year(tanggal):
    try:
        _, month, year = map(int, tanggal.split('/'))
        month_name = MONTH_NAMES_ID[month]
        return f"{month_name} {year}"
    except:
        return None

# Function to display sheet content for theater
def display_theater_content(service, spreadsheet_id, sheet_title):
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
    month_sections = {}
    current_month = None

    if len(grid_data) >= 1:
        title_row_1 = [cell.get('formattedValue', '') for cell in grid_data[1].get('values', [])]
    if len(grid_data) >= 2:
        headers = [cell.get('formattedValue', '') for cell in grid_data[2].get('values', [])]

    expected_headers = ['NO', 'Tanggal', 'Show', 'Setlist', 'Unit Song']
    if not headers:
        st.error("No headers found in the sheet (Row 2).")
        return None, None, None, None

    if headers != expected_headers:
        st.error(f"Header mismatch. Found: {headers}, Expected: {expected_headers}")
        return None, None, None, None

    # Parse data and group by month sections
    for i, row in enumerate(grid_data[2:], start=2):
        row_values = [cell.get('formattedValue', '') for cell in row.get('values', [])]
        while len(row_values) < len(headers):
            row_values.append('')

        # Check if this row is a month title (only first column has a value)
        if row_values[0] and all(val == '' for val in row_values[1:]):
            current_month = row_values[0]
            month_sections[current_month] = {'start_row': i + 1, 'rows': []}
        elif row_values[0] in headers:  # Skip header rows
            continue
        elif any(val for val in row_values) and current_month:  # Data row under a month
            month_sections[current_month]['rows'].append(row_values)
            data.append(row_values)

    return headers, data, month_sections, len(grid_data)

# Function to append new row for theater
def append_theater_row(service, spreadsheet_id, sheet_title, headers, data, month_sections, total_rows, new_row_data, apply_row_formatting, get_sheet_id):
    try:
        no, tanggal, show, setlist, unit_song = new_row_data
        month_year = get_month_year(tanggal)
        if not month_year:
            st.error("Could not determine month and year from the date.")
            return False

        # Get the sheet ID for formatting
        sheet_id = get_sheet_id(service, spreadsheet_id, sheet_title)
        if sheet_id is None:
            st.error("Could not retrieve sheet ID for formatting.")
            return False

        # Find the position to insert the new row
        if month_year in month_sections:
            last_row_idx = month_sections[month_year]['start_row'] + len(month_sections[month_year]['rows'])
            range_str = f"{sheet_title}!A{last_row_idx + 1}"
        else:
            last_row_idx = total_rows
            range_str = f"{sheet_title}!A{last_row_idx + 1}"
            month_row = [[month_year, "", "", "", ""]]
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_str,
                valueInputOption="RAW",
                body={"values": month_row}
            ).execute()
            apply_row_formatting(service, spreadsheet_id, sheet_id, last_row_idx + 1, is_header=False, sheet_name=sheet_title)

            range_str = f"{sheet_title}!A{last_row_idx + 2}"
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_str,
                valueInputOption="RAW",
                body={"values": [headers]}
            ).execute()
            apply_row_formatting(service, spreadsheet_id, sheet_id, last_row_idx + 2, is_header=True, sheet_name=sheet_title)

            range_str = f"{sheet_title}!A{last_row_idx + 3}"

        new_row = [no, tanggal, show, setlist, unit_song]
        st.write(f"Attempting to append row to: {range_str}")
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_str,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [new_row]}
        ).execute()

        return True
    except HttpError as e:
        st.error(f"HTTP Error appending row: {e}")
        st.error(f"Error details: {e.content.decode('utf-8') if e.content else 'No additional details'}")
        return False
    except Exception as e:
        st.error(f"General error appending row: {e}")
        return False

# Function to render the input form for theater
def theater_form(service, spreadsheet_id, sheet_title, headers, data, month_sections, total_rows):
    st.subheader(f"Add New Row to {sheet_title}")
    with st.form("add_row_form"):
        last_no = max([int(row[0]) for row in data if row[0].isdigit()] + [0])
        no = st.text_input("Number of Show", value=str(last_no + 1), help="Unique number for the show")
        tanggal = st.date_input("Tanggal", help="Date in DD/MM/YYYY format")
        if isinstance(tanggal, str):
            tanggal = tanggal.strftime("%d/%m/%Y")
        else:
            tanggal = tanggal.strftime("%d/%m/%Y")
        show = st.selectbox("Show Type", options=["Trainee", "Reguler"], help="Select the show type")
        setlist = st.selectbox("Setlist", options=["Aitakatta", "Pajama", "Ramune", "RKJ", "TWT"], help="Select the setlist")
        unit_song = st.text_area("Unit Song", help="Unit songs, one per line (e.g., - Song1\n- Song2)")
        new_row_data = (no, tanggal, show, setlist, unit_song)

        if st.form_submit_button("Submit"):
            if no and tanggal and show and setlist and unit_song:
                if not no.isdigit():
                    st.error("NO must be a number.")
                elif any(row[0] == no for row in data):
                    st.error(f"NO '{no}' already exists. Please use a unique value.")
                elif not validate_date(tanggal):
                    st.error("Tanggal must be in DD/MM/YYYY format with valid date.")
                else:
                    if append_theater_row(service, spreadsheet_id, sheet_title, headers, data, month_sections, total_rows, new_row_data, apply_row_formatting, get_sheet_id):
                        st.success(f"Successfully added new row with NO '{no}' under {get_month_year(tanggal)}.")
            else:
                st.warning("Please fill in all fields.")