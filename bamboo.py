from logger import logger
from conf import conf
from proxies import proxies
import requests
import json
import time

def get_bamboo_result(uri):
    try:
        if proxies:
            response = requests.get(uri, verify=False, proxies=proxies, timeout=10.0)
        else:
            response = requests.get(uri, verify=False, timeout=10.0)
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
    except Exception as e:
        # TODO: narrow this exception
        logger.error("Can't get info from Bamboo {0}:\n{1}".format(uri, e))
        return None


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

# TODO: add last downtime facility for Geckoboard
