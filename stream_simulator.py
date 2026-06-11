import json
import time
import requests
import os

# Point this to your FastAPI ingestion endpoint
API_URL = "http://localhost:8000/api/ingest"

# Point this to the SenAI dataset
DATA_FILE = os.path.join("data", "email-data-advanced.json")

def simulate_stream(delay_seconds=2.0):
    print(f"🚀 Starting streaming simulation from {DATA_FILE}...")
    
    try:
        with open(DATA_FILE, "r") as file:
            emails = json.load(file)
    except FileNotFoundError:
        print(f"❌ Error: Could not find {DATA_FILE}. Make sure the file exists.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: {DATA_FILE} is not a valid JSON file.")
        return

    print(f"📊 Found {len(emails)} emails. Beginning ingestion pipeline...\n")

    for index, email in enumerate(emails, start=1):
        print(f"📨 [{index}/{len(emails)}] Sending: '{email.get('subject', 'No Subject')}' from {email.get('sender')}")
        
        try:
            # Send the POST request to your FastAPI backend
            response = requests.post(API_URL, json=email)
            
            if response.status_code == 202:
                print(f"✅ Success: {response.json().get('classification', 'Classified')}")
            else:
                print(f"⚠️ Warning ({response.status_code}): {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: Could not connect to the API. Is your Docker container running?")
            break
            
        # Pause to simulate real-time traffic (and avoid rate-limiting the LLM)
        time.sleep(delay_seconds)

    print("\n🏁 Streaming simulation complete!")

if __name__ == "__main__":
    # You can change the delay here. 2 seconds is a safe speed for LLM API limits.
    simulate_stream(delay_seconds=2.0)