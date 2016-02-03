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

    @staticmethod
    def previous_connection_cache_key(uri):
        return 'BambooConnection:{uri}'.format(uri=uri)

    @staticmethod
    def previous_failure_count_cache_key(uri):
        return 'BambooConnection:{uri}'.format(uri=uri)

    def task_result(self, environment, job, uri):
        successfully_connected = self.get_connection_state(uri)
        try:
            if proxies:
                response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
            else:
                response = requests.get(uri, verify=False, timeout=10.0)
        except (RequestException, ConnectionError, MaxRetryError) as e:
            if successfully_connected:
                message = "Signaller '{signaller}': '{env}' Bamboo job '{job}' not responding, URI: '{uri}'\n" \
                          "No further warnings will be given unless/until it responds.\n"
                message += "Exception: {exception}\n"
                message = message.format(signaller="OMS",  env=environment, job=job, uri=uri, exception=e)
                logger.warning(message)
                self.store_connection_state(uri, False)
        else:
            self.store_connection_state(uri, True)
            logger.info("response {response} from {job} ({uri})"
                        .format(response=response.status_code, job=job, uri=uri))
            results = json.loads(response.text)
            logger.info("Tests passing({job}): {results}"
                        .format(job=job, results=results['successfulTestCount']))
            failures = results['failedTestCount']
            if failures:
                logger.warning("*** Tests failing ({job}): {failures} ***"
                    .format(job=job, failures=failures))
            else:
                logger.info("All active tests passed ({job})".format(job=job))
            logger.info("Skipped tests ({job}): {skipped}"
                        .format(job=job, skipped=results['skippedTestCount']))
            return results['successful']
        self.store_connection_state(uri, successfully_connected)

    def get_connection_state(self, uri):
        return State.retrieve(self.previous_connection_cache_key(uri), True)

    def store_connection_state(self, uri, was_connected):
        State.store(self.previous_connection_cache_key(uri), was_connected)

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
            if self.get_connection_state(uri):
                logger.info("{environment}: '{job}', Bamboo tag {tag}, result is '{result}'"
                            .format(environment=environment, job=job, tag=tag, result=result))
        return results
