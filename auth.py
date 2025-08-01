import base64
import os
from dotenv import load_dotenv, set_key
import requests
from pathlib import Path

load_dotenv(override=True)

## TO GET ACCESS IN THE FIRST PLACE
###############################################################################################################
## RUN THIS BLOCK FIRST, AND FIND THE CODE FROM THE URL OF THE CALLBACK LINK
# # The API endpoint
# url = "https://accounts.spotify.com/authorize?"

# # ## investigate this link
# params = {
#     "client_id": os.getenv("CLIENT_ID"),
#     "response_type" : 'code',
#     "redirect_uri" : "http://127.0.0.1:8888/callback",
#     "scope" : "user-read-recently-played user-read-playback-state user-read-currently-playing user-top-read user-read-email user-read-private"
# }

# # A GET request to the API
# response = requests.get(url,params=params)
# #headers={f"Authorization":f"Bearer  {os.getenv("ACCESS_TOKEN")}"}
# # # Print the response
# # print(response.json())
# print("here")
# print(response)
# print(response.url)


## USE THE CODE FROM THE URL OF THE CALLBACK LINK FOR THIS SECTION
# url = "https://accounts.spotify.com/api/token"

# data = {
# 'grant_type' : "authorization_code",
# 'code' : 'os.getenv("AUTH_CODE")',
# 'redirect_uri' : "http://127.0.0.1:8888/callback"}
# headers = { 'Authorization' : f'Basic {base64.b64encode(f"{os.getenv("CLIENT_ID")}:{os.getenv("CLIENT_SECRET")}".encode()).decode()}',
#            'Content-Type' : 'application/x-www-form-urlencoded'}

# response = requests.post(url,headers=headers,data=data)
# print(response.text)

###############################################################################################################

## TO REFRESH TOKEN
###############################################################################################################
headers = { 'Authorization' : f'Basic {base64.b64encode(f"{os.getenv("CLIENT_ID")}:{os.getenv("CLIENT_SECRET")}".encode()).decode()}',
       'Content-Type' : 'application/x-www-form-urlencoded'}
data = {
    'grant_type':'refresh_token',
   'refresh_token'	: os.getenv("REFRESH_TOKEN")
}

url = "https://accounts.spotify.com/api/token"
response = requests.post(url,headers=headers,data=data)
print(response.text)
set_key(Path('.') / '.env', 'ACCESS_TOKEN', response.json()['access_token'])
###############################################################################################################