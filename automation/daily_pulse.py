import os
import random
import uuid
import sys
from datetime import datetime, timedelta

# Safety check: Verify library is installed
try:
    from posthog import Posthog
except ImportError:
    print("ERROR: 'posthog' library not found. Run 'pip install posthog' first.")
    sys.exit(1)

# 1. SETUP & VALIDATION
api_key = os.environ.get("POSTHOG_API_KEY")

if not api_key:
    print("CRITICAL ERROR: POSTHOG_API_KEY is missing from environment variables.")
    sys.exit(1)

# Mask the key for logs but confirm it exists
print(f"Loaded API Key: {api_key[:4]}...{api_key[-4:]}")

# Use the exact EU host address as per PostHog documentation
ph_client = Posthog(
    project_api_key=api_key, 
    host='https://eu.i.posthog.com' 
)

# 2. THE TIME WINDOW
# Rolling 24-hour window from the exact second the script starts
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=24)

print(f"Generating events for window: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")

# --- THE SIMULATION ENGINE ---

# 1. Retention: 150 events spread across 50 users
users = [f"user_stk_{i}" for i in range(1, 51)] 
event_types = ['dashboard_viewed', 'report_created', 'paywall_viewed', 'settings_opened']

for _ in range(150):
    user = random.choice(users)
    event = random.choice(event_types)
    
    # Precise timing within the last 24h
    random_seconds = random.randint(0, 86400)
    event_time = end_time - timedelta(seconds=random_seconds)
    
    ph_client.capture(
        user, 
        event, 
        timestamp=event_time,
        properties={"source": "stk_automation_bot"}
    )

# 2. Growth: 3-8 new signups
new_signups = random.randint(3, 8)
print(f"Creating {new_signups} new users...")

for _ in range(new_signups):
    # UUID makes it unique so we don't duplicate users every day
    new_user_id = f"user_{end_time.strftime('%Y%m%d')}_{str(uuid.uuid4())[:4]}"
    
    signup_seconds = random.randint(0, 86400)
    signup_time = end_time - timedelta(seconds=signup_seconds)
    
    ph_client.capture(
        new_user_id, 
        "user_signed_up", 
        timestamp=signup_time,
        properties={"plan": "free", "source": "organic"}
    )

# 3. THE "FLUSH"
# This forces the script to hold until PostHog confirms receipt
print(f"✅ Queued {150 + new_signups} events. Flusing buffer...")

try:
    ph_client.flush()
    print("Data sent successfully to PostHog EU!")
except Exception as e:
    print(f"FAILED to send data: {e}")
    sys.exit(1)
