import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

# قراءة البيانات من المتغيرات البيئية
token = os.getenv("KOBO_TOKEN")
project_code = os.getenv("KOBO_PROJECT")
fields = os.getenv("KOBO_FIELDS").split(",")  # تحويلها لقائمة
google_creds_json = os.getenv("GOOGLE_CREDENTIALS")

if not google_creds_json:
    raise ValueError("GOOGLE_CREDENTIALS فارغ! تحقق من الـ Secret في GitHub")

# تحويل JSON من string إلى dict
google_creds_dict = json.loads(google_creds_json)

# تهيئة gspread باستخدام الـ credentials من dict
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(google_creds_dict, scopes=scopes)
client = gspread.authorize(creds)

# فتح الشيت (ضع key الشيت هنا)
sheet = client.open_by_key("1umgOioWym-PfidyddxIme192B8ALNg9JByzh7hN4WwE").sheet1

def get_nested_value(data, field):
    keys = field.split("/")
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, "")
        else:
            return ""
    return value

# تحميل البيانات من Kobo
url = f"https://kobo.unhcr.org/api/v2/assets/{project_code}/data/"
headers = {"Authorization": f"Token {token}"}

submissions = []
while url:
    resp = requests.get(url, headers=headers).json()
    submissions.extend(resp.get("results", []))
    url = resp.get("next")

if not submissions:
    print("لا توجد بيانات جديدة")
else:
    # مسح الشيت وإضافة الأعمدة
    sheet.clear()
    sheet.append_row(fields)

    for entry in submissions:
        row = [get_nested_value(entry, f.strip()) for f in fields]
        sheet.append_row(row)

    print(f"تم تحديث الشيت بنجاح، {len(submissions)} سجل.")
