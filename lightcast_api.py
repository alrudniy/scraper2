import requests
import json
import time


"""
    GET ACCESS TOKEN

Client ID: gl1y06faj3kfe09e
Secret: 9m4SJWgJ
Scope: emsi_open

curl --request POST \
  --url https://auth.emsicloud.com/connect/token \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data client_id=gl1y06faj3kfe09e \
  --data client_secret=9m4SJWgJ \
  --data grant_type=client_credentials \
  --data scope=emsi_open
  
  {"access_token":"eyJhbGciOiJSUzI1NiIsImtpZCI6IjNDNjZCRjIzMjBGNkY4RDQ2QzJERDhCMjI0MEVGMTFENTZEQkY3MUYiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJQR2FfSXlEMi1OUnNMZGl5SkE3eEhWYmI5eDgifQ.eyJuYmYiOjE3NDA4NDAzNDYsImV4cCI6MTc0MDg0Mzk0NiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20iLCJhdWQiOlsiZW1zaV9vcGVuIiwiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20vcmVzb3VyY2VzIl0sImNsaWVudF9pZCI6ImdsMXkwNmZhajNrZmUwOWUiLCJuYW1lIjoiQWxleCBSdWRuaWsiLCJjb21wYW55IjoiRHJldyBVbml2ZXJzaXR5IiwiZW1haWwiOiJhcnVkbml5QGRyZXcuZWR1IiwiaWF0IjoxNzQwODQwMzQ2LCJzY29wZSI6WyJlbXNpX29wZW4iXX0.TZvq6lGVOB97JjAyTOqURKH5gNroJ8OpPvF6q-m8E-ccC0XWE8V4X1YdPI3h7-oQBqBYzlA1WaHLb9iV9VBUimfw3p3f3KVhPy4Mrlo9H-aVqOslqk_HuIBWopNNynFRtFSYKmhZI5OCofKnnnKnNeGbxUKdwAMRuaCD3dQlp_nQz4e-RQcjWm4hZr-bS1r2m6oUlk5WLjOpxeqH7ftY-Y4TDXZ_EyaPy5QzYyYnBnISRUNa2jhXfR6mf4BifYpuPLwkc6QwEwZbvhYLZx5_eXHvAOERwbZ7RzyALlMLsPSN-STtrQxplVAYORqGr1eye216XBjTkOC57FTgKh9ciA"
  ,"expires_in":3600,"token_type":"Bearer","scope":"emsi_open"}

"""

# Get access token using client credentials
auth_url = "https://auth.emsicloud.com/connect/token"
auth_headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
auth_data = {
    "client_id": "gl1y06faj3kfe09e",
    "client_secret": "9m4SJWgJ",
    "grant_type": "client_credentials",
    "scope": "emsi_open"
}

auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
if auth_response.status_code == 200:
    token_data = auth_response.json()
    access_token = token_data.get("access_token")
    print("Access token retrieved successfully.")
else:
    print("Failed to retrieve access token.")
    print(auth_response.text)
    exit(1)

# Endpoint for the latest skills version
url = "https://emsiservices.com/skills/versions/latest/skills"

# Replace <ACCESS_TOKEN> with your actual access token.
headers = {
    "Authorization": f"Bearer {access_token}"
}

chunk_size = 15
offset = 0
all_skills = []


# Build query parameters with pagination (limit and offset)
querystring = {
    "limit": str(chunk_size),
    "offset": str(offset)
}

#response = requests.get(url, headers=headers, params=querystring)
#response = requests.get(url, headers=headers)

#search = "Engineering"
search = "Engineer"
querystring = {"q":search,"typeIds":"ST1,ST2,ST3","fields":"id,name,type,infoUrl","limit":"50000"}
response = requests.request("GET", url, headers=headers, params=querystring)
print(response.text)

if response.status_code != 200:
    print(f"Error: Received status code {response.status_code}")
    print(response.text)
    

# Assuming the API returns a JSON list of skills
skills = response.json()
    


# Save the aggregated skills to a JSON file
with open(f"skills_{search}.json", "w") as json_file:
    json.dump(skills, json_file, indent=4)

#print(f"Total skills retrieved: {len(all_skills)}")
print("Skills have been successfully saved to skills.json.")
