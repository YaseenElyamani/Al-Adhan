import json
import urllib3

url = 'http://ip-api.com/json'
http = urllib3.PoolManager()
response = http.request("GET", url)
data = json.loads(response.data.decode('utf-8'))  # Decode the response and load JSON

print(data)

IP = data['query']
city = data['city']
country = data['country']
region = data['regionName']

print(f"IP: {IP}, City: {city}, Country: {country}, Region: {region}")
