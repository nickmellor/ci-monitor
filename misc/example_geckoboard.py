import config
import requests
import sys
import json
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}


#send stuff to our geckoboard widget

#widget send format  example
# {
#   "status": "Up",
#   "downTime": "9 days ago",
#   "responseTime": "593 ms"
# }


#total payload  example
# {
#   "api_key": "222f66ab58130a8ece8ccd7be57f12e2",
#   "data": {
#      "item": [
#         { "text": "Visitors", "value": 4223 },
#         { "text": "", "value": 238 }
#       ]
#   }
# }

if len(sys.argv) > 1:
    status = sys.argv[1]
else:
    status = 'up'

payload = {
    "api_key": config.API_KEY,
    "data": {
        "status": status,
        "downTime": "GET DOWN",
        "responseTime": "instant"
    }
}

WIDGET_KEYS = {
    'widget1': '146729-85d97420-652c-4415-b529-ab8a393260ab',  # simple up-down device
}

#Widget push URL for WIDGET_KEYS['widget1']
url = "https://push.geckoboard.com/v1/send/" + config.WIDGET_KEYS['widget1']
print('sending to ',url)
r = requests.post(url, headers=headers, data=json.dumps(payload))

if r.status_code == 200:
    print('success!')
else:
    print('fail!')
print('returns ', r.content)
