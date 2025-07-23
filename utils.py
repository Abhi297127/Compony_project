import os
import json
import config
from google.oauth2 import service_account
from googleapiclient.discovery import build

def fetch_attendance_sheet():
    creds = service_account.Credentials.from_service_account_file(
        config.GOOGLE_CREDENTIALS_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=config.GOOGLE_SHEET_ID,
                               range='Daily Attendance').execute()
    values = result.get('values', [])
    return values

def validate_user_in_sheet(name, mobile, sheet_data):
    for row in sheet_data[1:]:
        if len(row) < 2:
            continue  # skip rows that don't have enough columns
        if row[0] == name and row[1] == mobile:
            return True
    return False

def get_user_attendance(mobile, sheet_data):
    for row in sheet_data[1:]:
        if row[1] == mobile:
            return {
                'name': row[0],
                'mobile': row[1],
                'attendance': row[2:-4],
                'present_count': row[-4],
                'absent_count': row[-3],
                'attendance_percent': row[-2],
                'salary': row[-1]
            }
    return None
