from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import MaxRetryError

from logger import logger
from conf import conf
from proxies import proxies
import requests
import json


class Bamboo:
    def __init__(self, settings):
        self.environments = settings['environments']
        self.proxies = conf['proxies']
        self.previous_connection_problem = False

    def task_result(self, uri):
        global previous_connection_problem
        try:
            if self.proxies:
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

    def results_all_environments(self):
        results = {}
        for env in self.environments:
            results[env] = self.environment_results(env)
        return results

    def environment_results(self, env):
        results = {}
        for ci_project, ci_tag in self.environments[env].items():
            uri = self.settings['uri'].format(tag=ci_tag)
            results.update({ci_project: self.task_result(uri)})
            logger.info("Project '{0}', Bamboo tag: {1}, result: {2}".format(ci_project, ci_tag, results))
        return results
