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
        'credentials.json',  # أو استخدم GOOGLE_CREDENTIALS من GitHub Actions
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet_id = "1umgOioWym-PfidyddxIme192B8ALNg9JByzh7hN4WwE"
    spreadsheet = client.open_by_key(spreadsheet_id)
    sheet = spreadsheet.sheet1

    print("تم فتح الشيت بنجاح")

    # قراءة كل الصفوف الموجودة
    existing_rows = sheet.get_all_values()
    
    if existing_rows and len(existing_rows) > 1 and "_submission_time" in fields:
        # الشيت فيها بيانات → نأخذ آخر وقت تحميل
        last_row = existing_rows[-1]
        last_time = last_row[fields.index("_submission_time")]
        print("آخر submission في الشيت:", last_time)

        url = f"https://kobo.unhcr.org/api/v2/assets/{project_code}/data/?_submission_time__gt={last_time}"
    else:
        # الشيت فارغة → تحميل كل البيانات
        print("الشيت فارغة أو لا تحتوي على _submission_time — سيتم تحميل كل البيانات")
        url = f"https://kobo.unhcr.org/api/v2/assets/{project_code}/data/"

        # إذا الشيت فارغة، أضف عناوين الأعمدة
        if not existing_rows:
            sheet.append_row(fields)

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

    print("عدد السجلات الجديدة:", len(submissions))

    if not submissions:
        print("لا يوجد بيانات جديدة")
        return

    # إضافة البيانات الجديدة
    for entry in submissions:
        row = [get_nested_value(entry, field.strip()) for field in fields]
        sheet.append_row(row)

    print("تم تحديث البيانات بنجاح")

if __name__ == "__main__":
    token = input("Enter TOKEN: ")
    project_code = input("Enter Project Code: ")
    fields = input("Enter fields separated by comma: ").split(",")

    create_and_update_sheet(token, project_code, fields)
