import requests
url = "https://alphaleaks.com//wp-json/jwt-auth/v1/token"
params = {"username": "alphaleaks_13giyi", "password": "Freelanceraccount01"}


resp = requests.post(url=url, params=params)
print(resp.json())