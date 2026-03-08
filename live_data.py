print("Script Started...")

import requests
import gspread
from google.oauth2.service_account import Credentials


def get_nested_value(data, field):
    keys = field.split("/")
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, "")
        else:
            return ""
    return value


def create_and_update_sheet(token, project_code, fields):

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_file(
        'credentials.json',
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet_id = "1umgOioWym-PfidyddxIme192B8ALNg9JByzh7hN4WwE"
    spreadsheet = client.open_by_key(spreadsheet_id)
    sheet = spreadsheet.sheet1

    print("تم فتح الشيت بنجاح")

    url = f"https://kobo.unhcr.org/api/v2/assets/{project_code}/data/"
    headers = {
        "Authorization": f"Token {token}",
        "Accept": "application/json"
    }

    submissions = []
    next_url = url

    while next_url:
        response = requests.get(next_url, headers=headers)
        data = response.json()
        submissions.extend(data.get("results", []))
        next_url = data.get("next")

    print("عدد السجلات:", len(submissions))

    sheet.clear()
    sheet.append_row(fields)

    for entry in submissions:
        row = [get_nested_value(entry, field.strip()) for field in fields]
        sheet.append_row(row)

    print("تم تحديث البيانات بنجاح")


if __name__ == "__main__":
    token = input("Enter TOKEN: ")
    project_code = input("Enter Project Code: ")
    fields = input("Enter fields separated by comma: ").split(",")

    create_and_update_sheet(token, project_code, fields)