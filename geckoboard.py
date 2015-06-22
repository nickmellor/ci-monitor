import requests
import json
from proxies import proxies

class Geckoboard:

    def __init__(self, monitored_environments):
        self.monitored_environments = monitored_environments

    def show_results(self, results):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        for env in self.monitored_environments:
            env_status = all(result for result in results[env].values())
            payload = {
                "api_key": '1cc8d5ca020cbd02b239f66389f1fefd',
                "data": {
                    "status": {None: 'down', False: 'down', True: 'up'}[env_status],
                    "downTime": "n/a",
                    "responseTime": "instant"
                }
            }

            WIDGET_KEYS = {
                'SIT': '146729-b35320bb-c355-405f-a228-71c5656a0709',  # simple up-down device
            }

            push_url = "https://push.geckoboard.com/v1/send/" + WIDGET_KEYS[env]
            print('sending to geckoboard for environment {0} at {1}'.format(env, push_url))
            try:
                r = requests.post(push_url, headers=headers, data=json.dumps(payload), proxies=proxies)
                if r.status_code == 200:
                    print('success!')
                else:
                    print('fail!')
            except Exception as e:  # TODO: narrow this exception filter
                print("Couldn't write to geckoboard")
                # raise e


