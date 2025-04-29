#!/usr/bin/env python
import requests
import json
import sys

# Replace with your backend URL and authentication credentials
BASE_URL = "http://localhost:8000/api"  # Adjust as needed
USERNAME = "your_username"
PASSWORD = "your_password"

# Login to get authentication token
def get_auth_token():
    response = requests.post(
        f"{BASE_URL}/auth/token/",
        data={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    return response.json()["access"]

# Test hashtag generator
def test_hashtag_generator(token, query="travel photography", platform="instagram", 
                           count=10, content_type="General Post", 
                           popularity_mix="balanced"):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "query": query,
        "platform": platform,
        "count": count,
        "content_type": content_type,
        "popularity_mix": popularity_mix
    }
    
    response = requests.post(
        f"{BASE_URL}/content/generate-hashtags/",
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

if __name__ == "__main__":
    print("Testing Hashtag Generator...")
    
    # Get arguments from command line if provided
    query = sys.argv[1] if len(sys.argv) > 1 else "travel photography"
    platform = sys.argv[2] if len(sys.argv) > 2 else "instagram"
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    # Get authentication token
    token = get_auth_token()
    
    # Test hashtag generator
    test_hashtag_generator(
        token=token,
        query=query,
        platform=platform,
        count=count
    )
    
    print("\nDone!") 