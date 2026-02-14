import os
import random
import uuid
from datetime import datetime, timedelta
from posthog import Posthog

# 1. SETUP
posthog = Posthog(
    project_api_key=os.environ.get("POSTHOG_API_KEY"), 
    host='https://eu.i.posthog.com' 
)

DAILY_NEW_USERS = random.randint(5, 12)  # 5-12 new people join today
TOTAL_ACTIVE_BASE = 150 # We simulate a pool of ~150 returning users
CONVERSION_RATE_DAILY = 0.02 # 2% chance a free user buys today

now = datetime.utcnow()
yesterday = now - timedelta(days=1)
print(f"Simulating Universe for {yesterday.date()}...")

# --- HELPER FUNCTIONS ---

def get_random_timestamp():
    """Returns a random second within the 'yesterday' window"""
    seconds = random.randint(0, 86400)
    return yesterday - timedelta(seconds=seconds)

def generate_event(user_id, event, props={}):
    """Captures event to PostHog"""
    posthog.capture(
        user_id, 
        event, 
        timestamp=get_random_timestamp(),
        properties=props
    )

# --- THE LOGIC ENGINE ---

# 1. GENERATE NEW SIGNUPS (The "Fresh Blood")
# They join, maybe onboard, maybe bounce.
for i in range(DAILY_NEW_USERS):
    user_id = f"user_{yesterday.strftime('%Y%m%d')}_{str(uuid.uuid4())[:4]}_free"
    
    # Event A: Signup (Guaranteed)
    generate_event(user_id, "user_signed_up", {"plan": "free", "source": "ads"})
    
    # Event B: Onboarding (80% chance)
    if random.random() < 0.8:
        generate_event(user_id, "onboarding_completed", {"time_taken": random.randint(60, 300)})
        
        # Event C: First Value (50% chance)
        if random.random() < 0.5:
             generate_event(user_id, "dashboard_created", {"widgets": 3})

    print(f"New User Born: {user_id}")

# 2. SIMULATE RETURNING USERS (The "Existing Population")
# We generate IDs that look like they joined in the past 60 days.
# We "decode" their ID to decide how they act today.

for i in range(TOTAL_ACTIVE_BASE):
    # a. Create a fake "History"
    days_ago = random.randint(1, 60)
    join_date = (yesterday - timedelta(days=days_ago)).strftime('%Y%m%d')
    
    # b. Assign a Persona (Weighted Probability)
    # 10% are Pro, 90% are Free
    is_pro = random.random() < 0.1
    plan_status = "pro" if is_pro else "free"
    
    user_id = f"user_{join_date}_{i}_{plan_status}"

    # c. DECISION: Does this user log in today? (Retention Curve)
    # New users (joined < 7 days ago) login 60% of the time
    # Old users (joined > 30 days ago) login 20% of the time
    login_prob = 0.6 if days_ago < 7 else 0.2
    
    if random.random() > login_prob:
        continue # They churned for today (No simulation)

    # d. ACTIVITY LOOP
    # If they logged in, they do 3-10 things
    num_actions = random.randint(3, 10)
    
    for _ in range(num_actions):
        # LOGIC: Pro users use advanced features, Free users hit paywalls
        if is_pro:
            possible_events = ['report_export_pdf', 'advanced_filter', 'team_invite', 'dashboard_viewed']
            event = random.choice(possible_events)
            generate_event(user_id, event, {"plan": "pro"})
        else:
            # Free User Logic
            possible_events = ['dashboard_viewed', 'settings_viewed', 'basic_filter']
            
            # 10% chance to hit paywall
            if random.random() < 0.1:
                event = "paywall_viewed"
                generate_event(user_id, event, {"trigger": "feature_lock"})
                
                # e. THE CONVERSION EVENT (Rare!)
                # If they hit the paywall, small chance they buy RIGHT NOW
                if random.random() < CONVERSION_RATE_DAILY:
                    generate_event(user_id, "subscription_started", {"mrr": 29, "plan": "pro"})
                    print(f"KA-CHING! User {user_id} just subscribed!")
                    break # Stop generating events, they are busy paying
            else:
                event = random.choice(possible_events)
                generate_event(user_id, event, {"plan": "free"})

print(f"Universe Simulation Complete. Data sent to PostHog.")
