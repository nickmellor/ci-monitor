import json

import requests
from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import MaxRetryError

from monitor import Monitor
from utils.logger import logger
from utils.persist import Persist
from utils.proxies import proxies


class Bamboo(Monitor):

    def __init__(self, indicator, settings):
        super().__init__()
        self.indicator = indicator
        self.settings = settings
        self.previous_connection = {}
        self.connection = {}
        self.previously_failed = {}
        self.results = {}
        self.previous_results = {}

    def poll(self):
        self.previous_results = self.results
        self.previous_connection = self.connection
        self.connection = {}
        self.previous_results = self.results
        self.results = {}
        template = self.settings.template
        for name, tag in self.settings.tasks.items():
            uri = template.format(tag=tag)
            self.results[name] = self.poll_bamboo_task(name, uri)
        connection_changed = self.previous_connection != self.connection
        results_changed = self.results != self.previous_results
        self.changed = connection_changed or results_changed
        self.changed = self.changed or self.results != and not self.changed

    def poll_bamboo_task(self, name, uri):
        try:
            if proxies:
                response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
            else:
                response = requests.get(uri, verify=False, timeout=10.0)
            connection_ok = True
        except (RequestException, ConnectionError, MaxRetryError) as e:
            self.connection_failed(name, e)
            connection_ok = False
            result = None
        else:
            result = self.parse_response(name, response)
            if self.previously_connected(name):
                logger.info("{indicator}: {task_name}: '{result}'"
                            .format(indicator=self.indicator, task_name=name,
                                    result='passed' if result else 'some failed tests'))
        self.connection[name] = connection_ok
        return result

    def previously_connected(self, name):
        return self.connection.get(name, True)
        # return Persist.retrieve(self.previous_connection_cache_key(uri), True)

    def connection_failed(self, name, e):
        if self.previously_connected(name):
            message = "{indicator}: {name} not responding\n" \
                      "No further warnings will be given unless/until it responds.\n"
            message += "Exception: {exception}\n"
            message = message.format(indicator=self.indicator, name=name, exception=e)
            logger.warning(message)

    def parse_response(self, name, response):
        logger.info("{indicator}: {job} response {status} from ({uri})"
                    .format(indicator=self.indicator, status=response.status_code, name=name))
        result = json.loads(response.text)
        logger.info("{job}: no of tests passing: {passing}".format(job=name, passing=result['successfulTestCount']))
        self.handle_failure(name, result)
        logger.info("{job}: skipped tests: {skipped}"
                    .format(job=name, skipped=result['skippedTestCount']))
        return result['successful']

    def handle_failure(self, name, result):
        failed = result['failedTestCount']
        if failed == 0:
            logger.info("{job}: All active tests passed".format(job=name))
        this_task_changed = failed != self.previously_failed[name]
        if this_task_changed:
            if failed != 0:
                logger.warning(
                    "{job}: *** Tests failing: {failing} ***\n"
                    "This message from Bamboo might be useful: '{reason}'\n"
                    "No further warnings will be given until number of failed tests changes"
                        .format(job=name, failing=failed, reason=result['buildReason']))
            else:
                logger.warning(" *** NEW!! Tests all passing! ({job}) ***\n".format(job=name))
            self.previously_failed[name] = failed
        self.changed = self.changed or this_task_changed