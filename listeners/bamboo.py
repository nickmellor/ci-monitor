import json

import requests
from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import MaxRetryError

from listener import Listener
from utils.logger import logger
from utils.proxies import proxies


class Bamboo(Listener):

    def __init__(self, indicator_name, listener_class, settings):
        super().__init__(indicator_name, listener_class, settings)
        self.previous_connection = {}
        self.connection = {}
        self.previously_failed = {}
        self.all_tests_pass = {}
        self.previous_results = {}

    def poll(self):
        self.previous_results = self.all_tests_pass
        # self.previous_connection = self.connection
        self.previous_results = self.all_tests_pass
        template = self.settings.template
        for name, tag in self.settings.tasks.items():
            uri = template.format(tag=tag)
            self.all_tests_pass[name] = self.poll_bamboo_task(name, uri)
            logger.debug("uri: '{0}'".format(uri))
        connection_changed = self.previous_connection != self.connection
        results_changed = self.all_tests_pass != self.previous_results
        self.changed = connection_changed or results_changed

    def tests_ok(self):
        return all(self.all_tests_pass.values())

    def comms_ok(self):
        # print(self.connection)
        return all(self.connection.values()) if self.connection else False

    def has_changed(self):
        return self.changed

    def poll_bamboo_task(self, name, uri):
        try:
            if proxies:
                response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
            else:
                response = requests.get(uri, verify=False, timeout=10.0)
            self.connection[name] = True
        except (RequestException, ConnectionError, MaxRetryError) as e:
            self.connection_failed(name, e)
            self.connection[name] = False
            result = None
        else:
            result = self.tests_pass(name, response)
            if self.previously_connected(name):
                logger.info("{indicator}: {task_name}: '{result}'"
                            .format(indicator=self.indicator_name, task_name=name,
                                    result='passed' if result else 'some failed tests'))
                self.previous_connection['name'] = False
        return result

    def previously_connected(self, name):
        if name in self.previous_connection:
            return self.previous_connection.get(name)
        else:
            self.previous_connection[name] = True
            return True

    def connection_failed(self, name, e):
        if self.previously_connected(name):
            message = "{indicator}: {name} not responding\n" \
                      "No further warnings will be given unless/until it responds.\n"
            message += "Exception: {exception}\n"
            message = message.format(indicator=self.indicator_name, name=name, exception=e)
            logger.warning(message)

    def tests_pass(self, name, response):
        logger.info("{indicator}: {name} response {status} from '{name}'"
                    .format(indicator=self.indicator_name, status=response.status_code, name=name))
        parsed_json = json.loads(response.text)
        logger.info("{job}: no of tests passing: {passing}".format(job=name, passing=parsed_json['successfulTestCount']))
        self.handle_failure(name, parsed_json)
        logger.info("{job}: skipped tests: {skipped}"
                    .format(job=name, skipped=parsed_json['skippedTestCount']))
        return parsed_json['successful']

    def handle_failure(self, name, result):
        failed = result['failedTestCount']
        this_task_changed = failed != self.previously_failed.get(name)
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
