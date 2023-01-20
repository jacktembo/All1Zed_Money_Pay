import requests
import json

r = requests.get('http://radiouniverse.jacktembo.com:8080/api/zm/stations')
print(r.json())
