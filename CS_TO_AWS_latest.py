# MaDE by Syaidinsem, Intern Awesome in March 2025 - August 2025
# Remember to change month 

import requests
import sys
import os
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

# Log for debugging etc
def log_failure(date_range, error_msg):
    with open("failed_batches.log", "a") as f:
        f.write(f"{date_range} - {error_msg}\n")

# Load environment variables from .env file
load_dotenv()

# Access the variables
URL = "https://apithunder.makecontact.space/GetRecording"
CS_API_KEY = os.getenv("CS_API_KEY")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION_NAME
)

# Check if file exists in S3 AWS
def file_exists_in_s3(s3_key):
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        return True
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise

# Download file to local
def download_file(file_url, filename):
    if not file_url or not file_url.startswith("http"):
        print(f"❌ Invalid URL: {file_url}, skipping...")
        return False
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"✅ Downloaded: {filename}")
        return True
    else:
        print(f"❌ Failed to download: {filename}")
        return False

# Upload to S3
def upload_to_s3(filename, s3_key):
    try:
        s3.upload_file(filename, BUCKET_NAME, s3_key)
        print(f"🚀 Uploaded to S3: {s3_key}")
        return True
    except Exception as e:
        print(f"❌ Failed to upload {filename} to S3: {e}")
        return False

# 🔎 Fetch from API
def fetch_recordings(fromdate, todate):
    print(f"🔍 Fetching recordings from {fromdate} to {todate}...")
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-api-key': CS_API_KEY
    }
    payload = f"fromdate={fromdate}&todate={todate}"
    try:
        response = requests.post(URL, headers=headers, data=payload)
        if response.status_code == 200:
            print("✅ API Response Received!")
            return response.json()
        else:
            print(f"⚠️ API Request Failed - Status Code: {response.status_code}")
            print("🔵 Response:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print("❌ API Error:", e)
        return None


    #Try again in case of fail
def safe_process_recordings(fromdate, todate, retries=3):
    for attempt in range(1, retries + 1):
        try:
            print(f"🌀 Attempt {attempt} for {fromdate} to {todate}")
            process_recordings(fromdate, todate)
            return  # Exit once successful
        except Exception as e:
            wait = 2 ** attempt
            print(f"⚠️ Error during processing: {e} | Retrying in {wait}s...")
            time.sleep(wait)
    log_failure(f"{fromdate} to {todate}", f"Failed after {retries} retries")
    print(f"❌ Gave up on {fromdate} to {todate} after {retries} retries.")
    
# Main processor ( Remember to change dates Here❗❗ )
def process_recordings(fromdate, todate):
    response = fetch_recordings(fromdate, todate)
    if not response or "recordings" not in response:
        print(f"❌ No valid recordings for {fromdate} - {todate}. Skipping...")
        return
    recordings = response["recordings"]
    for recording in recordings:
        if isinstance(recording, dict):
            file_url = recording.get("URL")
            call_id = recording.get("CallId")
            if not file_url or not call_id:
                print("⚠️ Missing URL or CallId, skipping...")
                continue
            filename = f"recording_{call_id}.mp3"
            s3_key = f"recordings/july_2025/{filename}"  # adjust folder name as needed
            if file_exists_in_s3(s3_key):
                print(f"⚠️ Already exists in S3: {s3_key}, skipping.")
                continue
            if download_file(file_url, filename):
                if upload_to_s3(filename, s3_key):
                    os.remove(filename)
                    print(f"🗑️ Deleted local file: {filename}")
                else:
                    print(f"⚠️ Keeping local file: {filename}")
        else:
            print("⚠️ Unexpected item:", recording)
    print(f"✅ Finished {fromdate} - {todate}!") 

# Loop through dates
start_date = datetime(2025, 7, 7)
end_date = datetime(2025, 7, 8)

try:
    current_date = start_date
    while current_date <= end_date:
        fromdate = current_date.strftime("%Y-%m-%d")
        todate = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
        safe_process_recordings(fromdate, todate)
        current_date += timedelta(days=1)
except Exception as e:
    error_msg = f"❌ Script error: {str(e)}"
    print(error_msg)
