## COPY EVERYTHING BELOW THIS LINE INTO PYTHON CONSOLE ##

import requests
import json

# Replace with your credentials
username = "your_username"
password = "your_password"
base_url = "http://localhost:8000/api"

# 1. Login and get token
print("Logging in...")
auth_response = requests.post(
    f"{base_url}/auth/token/",
    json={"username": username, "password": password}
)

if auth_response.status_code != 200:
    print(f"Login failed: {auth_response.status_code}")
    print(auth_response.text)
else:
    token = auth_response.json()["access"]
    print("Login successful!")

    # 2. Generate hashtags
    print("\nGenerating hashtags...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # You can modify these parameters
    data = {
        "query": "travel photography",
        "platform": "instagram",
        "count": 10,
        "content_type": "General Post",
        "popularity_mix": "balanced"
    }
    
    response = requests.post(
        f"{base_url}/content/generate-hashtags/",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\nGenerated Hashtags:")
        for hashtag in result.get("hashtags", []):
            print(f"#{hashtag['name']}")
        
        print(f"\nTokens used: {result.get('tokens_used', 'N/A')}")
    else:
        print(f"Request failed: {response.status_code}")
        print(response.text) 