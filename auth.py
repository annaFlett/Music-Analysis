import base64
import os
from dotenv import load_dotenv
import requests

load_dotenv()

## TO GET ACCESS IN THE FIRST PLACE
###############################################################################################################
## RUN THIS BLOCK FIRST, AND FIND THE CODE FROM THE URL OF THE CALLBACK LINK
# # The API endpoint
# url = "https://accounts.spotify.com/authorize?"

# ## investigate this link
# params = {
#     "client_id": os.getenv("CLIENT_ID"),
#     "response_type" : 'code',
#     "redirect_uri" : "http://127.0.0.1:8888/callback",
#     "scope" : "user-library-read"
# }

# # A GET request to the API
# response = requests.get(url,params=params)
# #headers={f"Authorization":f"Bearer  {os.getenv("ACCESS_TOKEN")}"}
# # Print the response
# # print(response.json())
# print("here")
# print(response)
# print(response.url)


## USE THE CODE FROM THE URL OF THE CALLBACK LINK FOR THIS SECTION
# url = "https://accounts.spotify.com/api/token"

# data = {
# 'grant_type' : "authorization_code",
# 'code' : 'AQCZvz_o1gqrKOIzMRw3xQ6xZ_1kgyASRcBrSRnM_DHYjk8xlzuSNlIoLe9tvr4TzUxO6WZSl2UUCuqOZwGn4Yi_04ENjkDjRJPy3R5OhgRyw6U933x_vtJHHmopdyszj1sMrULTirr3rdG7IKLA3pgvoyqja0NwC0Iw34s5CItbOZH0piwHj3DU7ILMZhaBsa_kv5o',
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
###############################################################################################################