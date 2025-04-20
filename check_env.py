import os

required_vars = [
    'GOOGLE_CLIENT_ID',
    'GOOGLE_CLIENT_SECRET',
    'FACEBOOK_CLIENT_ID',
    'FACEBOOK_CLIENT_SECRET',
    'LINKEDIN_CLIENT_ID',
    'LINKEDIN_CLIENT_SECRET',
    'TWITTER_API_KEY',  # Used for both TWITTER_CLIENT_ID
    'TWITTER_API_SECRET',  # Used for both TWITTER_CLIENT_SECRET
    'TWITTER_ACCESS_TOKEN',
    'TWITTER_ACCESS_TOKEN_SECRET',
    'INSTAGRAM_CLIENT_ID',
    'INSTAGRAM_CLIENT_SECRET',
    'TIKTOK_CLIENT_KEY',
    'TIKTOK_CLIENT_SECRET',
    'TELEGRAM_BOT_TOKEN',
    'FRONTEND_URL'
]

print("Checking environment variables...")
missing_vars = []
for var in required_vars:
    value = os.getenv(var)
    if value is None:
        missing_vars.append(var)
    else:
        print(f"✓ {var} is set")
        # Check if this is a Twitter credential that maps to CLIENT_ID/SECRET
        if var == 'TWITTER_API_KEY':
            print(f"✓ TWITTER_CLIENT_ID is set (mapped from {var})")
        elif var == 'TWITTER_API_SECRET':
            print(f"✓ TWITTER_CLIENT_SECRET is set (mapped from {var})")

if missing_vars:
    print("\nMissing environment variables:")
    for var in missing_vars:
        print(f"✗ {var} is not set")
else:
    print("\nAll required environment variables are set!") 