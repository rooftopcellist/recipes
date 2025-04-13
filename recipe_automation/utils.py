import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io

def get_category_path(category):
    root = "."
    fallback = "quick-meals"
    categories = {
        "baking": "baking",
        "cocktails": "cocktails",
        "desserts": "desserts",
        "dinner": "dinner",
        "brews": "brews",
        "meal prep": "meal-prep",
        "smoothies": "smoothies",
        "thanksgiving": "thanksgiving"
    }
    return os.path.join(root, categories.get(category.strip().lower(), fallback))

def extract_file_id(url):
    if "id=" in url:
        return url.split("id=")[-1].split("&")[0]
    elif "/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    return None

def download_image_from_drive(file_id, dest_path):
    creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=creds)

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(dest_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        _, done = downloader.next_chunk()
