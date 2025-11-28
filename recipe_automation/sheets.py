import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

def get_new_recipes(sheet_url):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).sheet1
    rows = sheet.get_all_records()

    with open("processed_recipes.json") as f:
        last_processed = datetime.fromisoformat(json.load(f)["last_processed"])

    new_rows = []
    for row in rows:
        try:
            timestamp = datetime.strptime(row["Timestamp"], "%m/%d/%Y %H:%M:%S")
            if timestamp > last_processed:
                row["__timestamp"] = timestamp
                new_rows.append(row)
        except Exception as e:
            print(f"Skipping row: {e}")

    return new_rows
