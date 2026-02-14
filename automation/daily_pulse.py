import os
import random
import uuid
import sys
from datetime import datetime, timedelta
from posthog import Posthog

# 1. ROBUST SETUP (The "Loud" Part)
api_key = os.environ.get("POSTHOG_API_KEY")

if not api_key:
    print("CRITICAL ERROR: POSTHOG_API_KEY is missing from environment variables.")
    sys.exit(1) # Fail the GitHub Action immediately

# Print masked key to verify it's reading the right secret
print(f"Loaded API Key: {api_key[:4]}...{api_key[-4:]}")

posthog = Posthog(
    project_api_key=api_key, 
    host='https://eu.i.posthog.com' # Confirmed EU Host
)

# 2. PRECISE TIME WINDOW (The "Sync Logic")
# We want data from [Now - 24h] to [Now]
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=24)

print(f"⏳ Generating events for window: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")

# --- THE SIMULATION ENGINE ---

# 1. Existing Users (Retention)
users = [f"user_stk_{i}" for i in range(1, 50)] 
event_types = ['dashboard_viewed', 'report_created', 'paywall_viewed', 'settings_opened']

for _ in range(150):
    user = random.choice(users)
    event = random.choice(event_types)
    
    # Logic: Pick a random second within the last 86400 seconds (24 hours)
    random_seconds = random.randint(0, 86400)
    event_time = end_time - timedelta(seconds=random_seconds)
    
    posthog.capture(
        user, 
        event, 
        timestamp=event_time,
        properties={"source": "stk_automation_bot"}
    )

# 2. New Signups (Growth)
new_signups = random.randint(3, 8)
print(f"Creating {new_signups} new users...")

for _ in range(new_signups):
    new_user_id = f"user_{end_time.strftime('%Y%m%d')}_{str(uuid.uuid4())[:4]}"
    
    # Signup happens sometime in the last 24h
    signup_seconds = random.randint(0, 86400)
    signup_time = end_time - timedelta(seconds=signup_seconds)
    
    posthog.capture(
        new_user_id, 
        "user_signed_up", 
        timestamp=signup_time,
        properties={"plan": "free", "source": "organic"}
    )

print(f"Queued {150 + new_signups} events. Sending to PostHog...")

# 3. FORCE SEND (The Fix)
# This forces the script to wait until data is actually sent.
try:
    posthog.flush()
    print("Data sent successfully!")
except Exception as e:
    print(f"FAILED to send data: {e}")
    sys.exit(1) # Fail the action so you see a Red X in GitHub
