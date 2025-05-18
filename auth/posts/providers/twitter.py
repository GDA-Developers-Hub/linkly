import requests
from requests_oauthlib import OAuth1

def post(text, social_token):
    try:
        token = social_token.token
        token_secret = social_token.token_secret
        app = social_token.app

        auth = OAuth1(
            app.client_id,              # consumer key
            app.secret,                 # consumer secret
            token,                      # access token
            token_secret                # access token secret
        )

        url = "https://api.twitter.com/2/tweets"
        payload = {"text": text}
        response = requests.post(url, json=payload, auth=auth)

        if response.status_code in [200, 201]:
            return {"success": True, "tweet_id": response.json().get("data", {}).get("id")}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}