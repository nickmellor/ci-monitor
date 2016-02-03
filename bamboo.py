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

    def bamboo_job_result(self, environment, job, uri):
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
            return None
        else:
            self.store_connection_state(uri, True)
            logger.info("response {response} from {job} ({uri})"
                        .format(response=response.status_code, job=job, uri=uri))
            results = json.loads(response.text)
            logger.info("Tests passing({job}): {results}"
                        .format(job=job, results=results['successfulTestCount']))
            failures = results['failedTestCount']
            if failures != self.previous_failure_count(uri):
                if failures != 0:
                    logger.warning(
                        "{job}: *** Tests failing: {failures} ***\n"
                        "No further warnings will be given until number of failures changes"
                            .format(job=job, failures=failures))
                else:
                    logger.warning("*** NEW!! Tests all passing! ({job}) ***\n".format(job=job))
                self.store_failure_count(uri, failures)
            else:
                logger.info("All active tests passed ({job})".format(job=job))
            logger.info("{job}: skipped tests: {skipped}"
                        .format(job=job, skipped=results['skippedTestCount']))
            return results['successful']

    def get_connection_state(self, uri):
        return State.retrieve(self.previous_connection_cache_key(uri), True)

    def store_connection_state(self, uri, was_connected):
        State.store(self.previous_connection_cache_key(uri), was_connected)

    def previous_failure_count(self, uri):
        return State.retrieve(self.previous_failures_cache_key(uri), 0)

    def store_failure_count(self, uri, n):
        State.store(self.previous_failures_cache_key(uri), n)

    @staticmethod
    def previous_failures_cache_key(uri):
        return 'BambooFailures:{uri}'.format(uri=uri)

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
            result = self.bamboo_job_result(environment, job, uri)
            results.update({job: result})
            if self.get_connection_state(uri):
                logger.info("{environment}: '{job}', Bamboo tag {tag}, result is '{result}'"
                            .format(environment=environment, job=job, tag=tag, result='passed' if result else 'failed tests'))
        return results
