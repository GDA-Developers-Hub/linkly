#!/usr/bin/env python
import requests
import json

def test_hashtag_generator(username, password, query="travel photography", 
                          platform="instagram", count=10):
    """
    Test the hashtag generator from the console.
    
    Usage:
        # 1. Run this script in the Python console
        exec(open('test_console.py').read())
        
        # 2. Call the function with your credentials
        test_hashtag_generator('your_username', 'your_password', 'food photography')
    """
    base_url = "http://localhost:8000/api"
    
    # Get authentication token
    print(f"Logging in as {username}...")
    auth_response = requests.post(
        f"{base_url}/auth/token/",
        json={"username": username, "password": password}
    )
    
    if auth_response.status_code != 200:
        print(f"Login failed: {auth_response.status_code}")
        print(auth_response.text)
        return
    
    token = auth_response.json()["access"]
    print("Login successful!")
    
    # Generate hashtags
    print(f"\nGenerating hashtags for: '{query}' on {platform}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "query": query,
        "platform": platform,
        "count": count,
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

# Instructions:
if __name__ == "__main__":
    print("""
    To test the hashtag generator:
    
    1. Import this file in your Python console:
       >>> exec(open('test_console.py').read())
    
    2. Call the function with your credentials:
       >>> test_hashtag_generator('your_username', 'your_password', 'food photography')
    
    Optional parameters:
    - query: Keywords for generating hashtags (default: "travel photography")
    - platform: Social platform (default: "instagram")
    - count: Number of hashtags (default: 10)
    """) 