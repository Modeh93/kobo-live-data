import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

# ===== إعداد Google Sheets =====
SPREADSHEET_NAME = "live_Data test"

# قراءة بيانات الـ Service Account من GitHub Secret
creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

# تحديد الصلاحيات المطلوبة
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# إنشاء Credentials وتخويل gspread
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
gc = gspread.authorize(creds)

# فتح الشيت
sheet = gc.open(SPREADSHEET_NAME).sheet1

# ===== إعداد Kobo API =====
KOBO_TOKEN = os.environ["KOBO_TOKEN"]
KOBO_PROJECT = os.environ["KOBO_PROJECT"]
KOBO_FIELDS = os.environ["KOBO_FIELDS"]  # مثلا "_uuid"

BASE_URL = f"https://kobo.unhcr.org/api/v2/assets/{KOBO_PROJECT}/data/"

# ===== جلب البيانات =====
params = {
    "format": "json",
    "query": json.dumps({KOBO_FIELDS: {"$exists": True}})
}

headers = {"Authorization": f"Token {KOBO_TOKEN}"}
response = requests.get(BASE_URL, headers=headers, params=params)
response.raise_for_status()
data_json = response.json()

# تحقق من المفتاح 'results' إذا موجود
data = data_json.get("results", [])

print(f"عدد السجلات المسترجعة من Kobo: {len(data)}")

if not data:
    print("لا توجد بيانات جديدة للتحميل.")
else:
    # مسح القديم ثم كتابة الجديد
    sheet.clear()

    # كتابة العناوين
    headers = list(data[0].keys())
    sheet.append_row(headers)

    # كتابة الصفوف
    for row in data:
        sheet.append_row([row.get(h, "") for h in headers])

    print(f"تم تحديث {len(data)} سجلات في الشيت.")
