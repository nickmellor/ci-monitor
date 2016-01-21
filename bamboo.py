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
        self.previous_connection_problem = False
        # self.previous_connection_problem = State.retrieve(self.previous_connection_storage_id())
        # TODO: wire Bamboo into the config for specific Bamboo tasks (currently hard-wired to OMS)

    def previous_connection_storage_id(self):
        pass


    def task_result(self, uri):
        global previous_connection_problem
        try:
            if proxies:
                response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
            else:
                response = requests.get(uri, verify=False, timeout=10.0)
        except (RequestException, ConnectionError, MaxRetryError) as e:
            if not self.previous_connection_problem:
                message = "Signaller '{signaller}': Bamboo URI '{uri}' is not responding.\n" \
                          "No further warnings will be given\n"
                message += "Exception: {exception}\n"
                message = message.format(signaller="OMS",  uri=uri, exception=e)
                logger.warning(message)
            previous_connection_problem = True
        else:
            self.previous_connection_problem = False
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

    def all_results(self):
        results = {}
        for env, detail in self.settings['environments'].items():
            results[env] = self.environment_results(detail)
        return results

    def environment_results(self, bamboo_detail):
        results = {}
        uri_template = bamboo_detail.get('uri')
        for task, ci_tag in bamboo_detail['tasks'].items():
            uri = uri_template.format(tag=ci_tag)
            results.update({task: self.task_result(uri)})
            logger.info("Project '{0}', Bamboo tag: {1}, result: {2}".format(task, ci_tag, results))
        return results
