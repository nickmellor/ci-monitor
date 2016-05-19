import json

import requests
from utils.logger import logger
from utils.persist import Persist
from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import MaxRetryError

from utils.proxies import proxies


class Bamboo:

    def __init__(self, indicator, settings):
        self.indicator = indicator
        self.settings = settings

    def poll(self):
        results = {}
        template = self.settings.template
        for name, tag in self.settings.tasks.items():
            uri = template.format(tag=tag)
            results.update(self.poll_bamboo_task(name, uri))
        return all(results.values())

    def poll_bamboo_task(self, name, uri):
        try:
            if proxies:
                response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
            else:
                response = requests.get(uri, verify=False, timeout=10.0)
        except (RequestException, ConnectionError, MaxRetryError) as e:
            return self.connection_failed(e, self.indicator, name, uri)
        else:
            result = self.process_bamboo_results(name, response, uri)
            if self.previously_connected(uri):
                logger.info("{environment}: {task_name}: {tag}, '{result}'"
                            .format(environment=name, job=task_name, tag=tag,
                                    result='passed' if result else 'some failed tests'))
            return result

    def previously_connected(self, uri):
        return Persist.retrieve(self.previous_connection_cache_key(uri), True)

    def connection_failed(self, e, environment, job, uri):
        if self.previously_connected(uri):
            message = "Indicator '{indicator}': {env}: {job} not responding, URI: '{uri}'\n" \
                      "No further warnings will be given unless/until it responds.\n"
            message += "Exception: {exception}\n"
            message = message.format(signal="OMS", env=environment, job=job, uri=uri, exception=e)
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
                    "Is this useful? {reason}\n"
                    "No further warnings will be given until number of failures changes"
                        .format(job=job, failing=failures, reason=results['buildReason']))
            else:
                logger.warning("*** NEW!! Tests all passing! ({job}) ***\n".format(job=job))
            self.store_failure_count(uri, failures)

    @staticmethod
    def previous_connection_cache_key(uri):
        return 'BambooConnection:{uri}'.format(uri=uri)

    def store_connection_state(self, uri, was_connected):
        Persist.store(self.previous_connection_cache_key(uri), was_connected)

    def previous_failure_count(self, uri):
        return Persist.retrieve(self.previous_failures_cache_key(uri), 0)

    def store_failure_count(self, uri, n):
        Persist.store(self.previous_failures_cache_key(uri), n)

    @staticmethod
    def previous_failures_cache_key(uri):
        return 'BambooFailures:{uri}'.format(uri=uri)