import requests
from pprint import pprint
import json
url = 'https://api.github.com/users/nadvlasova/repos'

req = requests.get(url)
# repos = req.headers
# repos = req.headers.get('public')
# name = repos.get('public')

with open('data.json', 'w') as f:
    json.dump(req.json(), f)

for i in req.json():
    print(i['name'])
pprint(req)