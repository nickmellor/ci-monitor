import requests
import json
from proxies import proxies
from logger import logger
from conf import conf

class Geckoboard:

    def __init__(self, monitored):
        self.monitored_environments = monitored

    def show_results(self, results):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        for env in self.monitored_environments:
            env_status = all(result for result in results[env].values())
            payload = {
                "api_key": conf['geckoboard']['apikey'],
                "data": {
                    "status": {None: 'down', False: 'down', True: 'up'}[env_status],
                    "downTime": "n/a",
                    "responseTime": "instant"
                }
            }
            push_url = "https://push.geckoboard.com/v1/send/" + conf['geckoboard']['widgetkeys'][env]
            logger.info('sending to geckoboard for environment {0} at {1}'.format(env, push_url))
            try:
                r = requests.post(push_url, headers=headers, data=json.dumps(payload), proxies=proxies)
                if r.status_code == 200:
                    logger.info('success!')
                else:
                    logger.warning('Did not succeed sending to Geckoboard (env={0})'.format(env))
            except Exception as e:  # TODO: narrow this exception filter
                logger.error("Couldn't write to geckoboard. Exception follows: \n{0}".format(e))
