from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import MaxRetryError

from logger import logger
from conf import conf
from proxies import proxies
import requests
import json

previous_connection_problem = False


class Bamboo:
    pass

def get_bamboo_result(uri):
    global previous_connection_problem
    try:
        if proxies:
            response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
        else:
            response = requests.get(uri, verify=False, timeout=10.0)
    except (RequestException, ConnectionError, MaxRetryError) as e:
        if not previous_connection_problem:
            message = "Signaller '{signaller}': Bamboo URI is not responding.\n" \
                      "No further warnings will be given\n"
            message += "Exception: '{exception}'\n"
            message = message.format(signaller="OMS",  exception=e)
            logger.warning(message)
            # logger.error("Signaller {signaller}: can't get info from Bamboo:\n{exception}".format(signaller=self.signal_name, exception=e))
    else:
        previous_connection_problem = False
        logger.info("response from {0}".format(uri))
        logger.info(response.status_code)
        results = json.loads(response.text)
        logger.info("Tests passing: {0}".format(results['successfulTestCount']))
        failures = results['failedTestCount']
        if failures:
            logger.info("Failed tests: {0}".format(failures))
        else:
            logger.info("*** All active tests passed ({0}) ***".format(results['successful']))
        logger.info("Skipped tests: {0}".format(results['skippedTestCount']))
        return results['successful']


def collect_bamboo_data():
    ci_environments = conf['bamboo']['environments']
    results = {}
    for env in ci_environments:
        env_results = {}
        for project, ci_tag in ci_environments[env].items():
            uri = conf['bamboo']['uri'].format(tag=ci_tag)
            env_results.update({project: get_bamboo_result(uri)})
            logger.info("env: {0} tag: {1} success: {2}".format(project, ci_tag, env_results))
        results[env] = env_results
    return results
