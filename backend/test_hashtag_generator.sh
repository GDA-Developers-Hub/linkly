#!/bin/bash

# Replace with your backend URL and authentication credentials
BASE_URL="http://localhost:8000/api"  # Adjust as needed
USERNAME="your_username"
PASSWORD="your_password"

# Get authentication token
echo "Getting authentication token..."
TOKEN_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/auth/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}")

# Extract token from response
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to get access token. Response:"
  echo $TOKEN_RESPONSE
  exit 1
fi

echo "Token obtained successfully."

# Default values
QUERY=${1:-"travel photography"}
PLATFORM=${2:-"instagram"}
COUNT=${3:-10}
CONTENT_TYPE="General Post"
POPULARITY_MIX="balanced"

# Test hashtag generator
echo "Testing hashtag generator with query: $QUERY, platform: $PLATFORM, count: $COUNT..."
curl -X POST \
  "${BASE_URL}/content/generate-hashtags/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"${QUERY}\",
    \"platform\": \"${PLATFORM}\",
    \"count\": ${COUNT},
    \"content_type\": \"${CONTENT_TYPE}\",
    \"popularity_mix\": \"${POPULARITY_MIX}\"
  }" | json_pp

echo -e "\nDone!" 