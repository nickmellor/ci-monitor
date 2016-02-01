from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import MaxRetryError

from logger import logger
from proxies import proxies
import requests
import json
from state import State


class Bamboo:
    """
    retrieve Bamboo results for a signaller's monitored environments
    """

    def __init__(self, settings):
        self.settings = settings
        self.environments = settings['environments']
        self.was_connected = {}

    @staticmethod
    def previous_connection_storage_id(uri):
        return 'Bamboo:{uri}'.format(uri=uri)

    def task_result(self, environment, job, uri):
        self.was_connected[uri] = State.retrieve(self.previous_connection_storage_id(uri), True)
        try:
            if proxies:
                response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
            else:
                response = requests.get(uri, verify=False, timeout=10.0)
        except (RequestException, ConnectionError, MaxRetryError) as e:
            if self.was_connected[uri]:
                message = "Signaller '{signaller}': '{env}' Bamboo job '{job}' not responding, URI: '{uri}'\n" \
                          "No further warnings will be given unless/until it responds.\n"
                message += "Exception: {exception}\n"
                message = message.format(signaller="OMS",  env=environment, job=job, uri=uri, exception=e)
                logger.warning(message)
                self.was_connected[uri] = False
        else:
            self.was_connected[uri] = True
            logger.info("response from {0}".format(uri))
            logger.info(response.status_code)
            results = json.loads(response.text)
            logger.info("Tests passing({job}): {results}"
                        .format(job=job, results=results['successfulTestCount']))
            failures = results['failedTestCount']
            if failures:
                logger.info("Tests failing ({job}): {results}"
                            .format(job=job, failures=failures))
            else:
                logger.info("*** All active tests passed ({job})***".format(job=job))
            logger.info("Skipped tests ({job}): {skipped}"
                        .format(job=job, skipped=results['skippedTestCount']))
            return results['successful']
        State.store(self.previous_connection_storage_id(uri), self.was_connected[uri])

    def all_results(self):
        results = {}
        for env, detail in self.settings['environments'].items():
            results[env] = self.environment_results(env, detail)
        return results

    def environment_results(self, environment, bamboo_detail):
        results = {}
        uri_template = bamboo_detail.get('uri')
        for job, tag in bamboo_detail['jobs'].items():
            uri = uri_template.format(tag=tag)
            result = self.task_result(environment, job, uri)
            results.update({job: result})
            if self.was_connected.get(uri):
                logger.info("{environment}: '{job}', Bamboo tag {tag}, result is '{result}'"
                            .format(environment=environment, job=job, tag=tag, result=result))
        return results
