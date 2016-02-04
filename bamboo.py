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
        try:
            if proxies:
                response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
            else:
                response = requests.get(uri, verify=False, timeout=10.0)
        except (RequestException, ConnectionError, MaxRetryError) as e:
            return self.connection_failed(e, environment, job, uri)
        else:
            return self.process_bamboo_results(job, response, uri)

    def connection_failed(self, e, environment, job, uri):
        if self.previously_connected(uri):
            message = "Signaller '{signaller}': {env}: {job} not responding, URI: '{uri}'\n" \
                      "No further warnings will be given unless/until it responds.\n"
            message += "Exception: {exception}\n"
            message = message.format(signaller="OMS", env=environment, job=job, uri=uri, exception=e)
            logger.warning(message)
            self.store_connection_state(uri, False)
        return None

    def process_bamboo_results(self, job, response, uri):
        self.store_connection_state(uri, True)
        logger.info("{job}: response {response} from ({uri})"
                    .format(response=response.status_code, job=job, uri=uri))
        results = json.loads(response.text)
        logger.info("{job}: no of tests passing: {passing}".format(job=job, passing=results['successfulTestCount']))
        self.handle_recurring_failures(job, uri, results)
        logger.info("{job}: skipped tests: {skipped}"
                    .format(job=job, skipped=results['skippedTestCount']))
        return results['successful']

    def handle_recurring_failures(self, job, uri, results):
        failures = results['failedTestCount']
        if failures == 0:
            logger.info("{job}: All active tests passed".format(job=job))
        if failures != self.previous_failure_count(uri):
            if failures != 0:
                logger.warning(
                    "{job}: *** Tests failing: {failing} ***\n"
                    "No further warnings will be given until number of failures changes"
                        .format(job=job, failing=failures))
            else:
                logger.warning("*** NEW!! Tests all passing! ({job}) ***\n".format(job=job))
            self.store_failure_count(uri, failures)

    def previously_connected(self, uri):
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
            if self.previously_connected(uri):
                logger.info("{environment}: {job}: {tag}, '{result}'"
                            .format(environment=environment, job=job, tag=tag,
                                    result='passed' if result else 'some failed tests'))
        return results
