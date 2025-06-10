# backend/api/utils/supabase_client.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

def upload_to_supabase(filepath, filename):
    try:
        with open(filepath, 'rb') as f:
            file_data = f.read()

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }

        upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
        res = requests.put(upload_url, headers=headers, data=file_data)

        if res.status_code in [200, 201]:
            return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        else:
            raise Exception(f"Supabase upload failed. Status: {res.status_code}, Response: {res.text}")
    except Exception as e:
        raise Exception(f"Supabase upload exception: {str(e)}")

