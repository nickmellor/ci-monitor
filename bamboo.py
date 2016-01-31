from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import MaxRetryError

from logger import logger
from conf import conf
from proxies import proxies
import requests
import json
from state import State


class Bamboo:
    def __init__(self, settings):
        self.settings = settings
        self.environments = settings['environments']
        self.was_connected = State.retrieve(self.previous_connection_storage_id(), True)

    def previous_connection_storage_id(self):
        return 'Bamboo:{environments}'.format(environments=','.join(self.settings['environments'].keys()))

    def task_result(self, uri):
        try:
            if proxies:
                response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
            else:
                response = requests.get(uri, verify=False, timeout=10.0)
        except (RequestException, ConnectionError, MaxRetryError) as e:
            if self.was_connected:
                message = "Signaller '{signaller}': Bamboo URI not responding, URI: '{uri}'\n" \
                          "No further warnings will be given unless/until it responds.\n"
                message += "Exception: {exception}\n"
                message = message.format(signaller="OMS",  uri=uri, exception=e)
                logger.warning(message)
                self.was_connected = False
        else:
            self.was_connected = True
            logger.info("response from {0}".format(uri))
            logger.info(response.status_code)
            results = json.loads(response.text)
            logger.info("Tests passing: {0}".format(results['successfulTestCount']))
            failures = results['failedTestCount']
            if failures:
                logger.info("Tests failing: {0}".format(failures))
            else:
                logger.info("*** All active tests passed ***".format(results['successful']))
            logger.info("Skipped tests: {0}".format(results['skippedTestCount']))
            return results['successful']
        State.store(self.previous_connection_storage_id(), self.was_connected)

    def all_results(self):
        results = {}
        for env, detail in self.settings['environments'].items():
            results[env] = self.environment_results(env, detail)
        return results

    def environment_results(self, environment, bamboo_detail):
        results = {}
        uri_template = bamboo_detail.get('uri')
        for job, ci_tag in bamboo_detail['tasks'].items():
            uri = uri_template.format(tag=ci_tag)
            result = self.task_result(uri)
            results.update({job: result})
            if self.was_connected:
                logger.info("{environment}: '{job}', Bamboo tag {tag}, result is '{result}'"
                            .format(environment=environment, job=job, tag=ci_tag, result=result))
        return results
