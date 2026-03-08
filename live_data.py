import os

# قراءة البيانات من المتغيرات البيئية
token = os.getenv("KOBO_TOKEN")
project = os.getenv("KOBO_PROJECT")
fields = os.getenv("KOBO_FIELDS")
google_creds = os.getenv("GOOGLE_CREDENTIALS")

# تحويل JSON Google credentials من string إلى dict إذا كنت تستخدمه مع gspread
import json
google_creds_dict = json.loads(google_creds)

# الآن استخدم token وproject وfields في الكود بدل input()
print("Token:", token)
print("Project:", project)
print("Fields:", fields)
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
    creds = Credentials.from_service_account_file('credentials.json', scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ])
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1umgOioWym-PfidyddxIme192B8ALNg9JByzh7hN4WwE").sheet1

    # تحميل جميع البيانات
    url = f"https://kobo.unhcr.org/api/v2/assets/{project_code}/data/"
    headers = {"Authorization": f"Token {token}"}

    submissions = []
    while url:
        resp = requests.get(url, headers=headers).json()
        submissions.extend(resp.get("results", []))
        url = resp.get("next")

    if not submissions:
        print("لا توجد بيانات")
        return

    # مسح الشيت وإضافة الأعمدة
    sheet.clear()
    sheet.append_row(fields)

    for entry in submissions:
        row = [get_nested_value(entry, f.strip()) for f in fields]
        sheet.append_row(row)

    print(f"تم تحديث الشيت بنجاح، {len(submissions)} سجل.")

if __name__ == "__main__":
    token = input("Enter TOKEN: ")
    project_code = input("Enter Project Code: ")
    fields = input("Enter fields separated by comma: ").split(",")

    create_and_update_sheet(token, project_code, fields)

