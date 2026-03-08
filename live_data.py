import gspread
from google.oauth2.service_account import Credentials
import requests
import json
import os

# --- إعدادات Google Sheets ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
creds_dict = json.loads(creds_json)
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
gc = gspread.authorize(creds)

# اسم الشيت
SPREADSHEET_NAME = "Kobo Live Data"
sheet = gc.open(SPREADSHEET_NAME).sheet1

# --- إعدادات Kobo ---
KOBO_TOKEN = os.environ.get("KOBO_TOKEN")
KOBO_PROJECT = os.environ.get("KOBO_PROJECT")
KOBO_FIELDS = os.environ.get("KOBO_FIELDS")  # مثال: "_uuid"

KOBO_URL = f"https://kf.kobotoolbox.org/api/v2/assets/{KOBO_PROJECT}/data/"

headers = {
    "Authorization": f"Token {KOBO_TOKEN}"
}

# --- جلب آخر uuid موجود في الشيت ---
existing_uuids = sheet.col_values(1)  # افترض أن العمود الأول فيه _uuid
last_uuid = existing_uuids[-1] if len(existing_uuids) > 1 else None

# --- إعداد الفلتر للبيانات الجديدة ---
params = {}
if last_uuid:
    # سيجلب فقط السجلات الجديدة بعد آخر uuid موجود
    params["query"] = json.dumps({KOBO_FIELDS: {"$gt": last_uuid}})

# --- جلب البيانات من Kobo ---
response = requests.get(KOBO_URL, headers=headers, params=params)
data = response.json()

if "results" not in data or len(data["results"]) == 0:
    print("لا توجد بيانات جديدة")
else:
    print(f"تم جلب {len(data['results'])} سجلات جديدة")
    rows_to_add = []
    for entry in data["results"]:
        row = [entry.get(KOBO_FIELDS, "")]  # العمود الأساسي _uuid
        # إضافة باقي الحقول إذا أردت
        for key, value in entry.items():
            if key != KOBO_FIELDS:
                row.append(value)
        rows_to_add.append(row)

    # إضافة البيانات الجديدة للشيت
    for row in rows_to_add:
        sheet.append_row(row)
    print("تم تحديث الشيت بالبيانات الجديدة")
