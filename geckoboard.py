import requests
import json
from proxies import proxies
from logger import logger
from conf import configuration


class Geckoboard:

    def __init__(self):
        self.monitored_environments = configuration['geckoboard']['bamboo_environments'] if configuration.get('geckoboard') else None

    def show_monitored_environments(self, results):
        if self.monitored_environments:
            self.show_results(results)

    def show_results(self, results):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        for env in self.monitored_environments:
            env_status = all(result for result in results[env].values())
            try:
                payload = {
                    "api_key": configuration['geckoboard']['apikey'],
                    "data": {
                        "status": {None: 'down', False: 'down', True: 'up'}[env_status],
                        "downTime": "n/a",
                        "responseTime": "instant"
                    }
                }
            except KeyError as e:
                logger.info('Problem with Geckoboard config. Exception follows: \n{0}'.format(e))
            push_url = "https://push.geckoboard.com/v1/send/" + configuration['geckoboard']['bamboo_widgets'][env]
            logger.info('sending to geckoboard for environment {0} at {1}'.format(env, push_url))
            try:
                if proxies:
                    r = requests.post(push_url, headers=headers, data=json.dumps(payload), proxies=proxies)
                else:
                    r = requests.post(push_url, headers=headers, data=json.dumps(payload))
                if r.status_code == 200:
                    logger.info('Push to Geckoboard succeeded!')
                else:
                    logger.warning('Did not succeed sending to Geckoboard (env={0})'.format(env))
            except ConnectionError as e:
                logger.error("Couldn't write to geckoboard. Exception follows: \n{0}".format(e))


# TODO: geckoboard: display a few failing tests (+ most recent committers?)
# TODO: add last downtime facility for Geckoboard
# TODO: enable one CI-monitor to look after more than one Geckoboard widget