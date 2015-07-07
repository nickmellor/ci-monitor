import datetime
from logger import logger
from conf import conf
from proxies import proxies
import requests
import json
import warnings

ci_environments = conf['bamboo']['environments']

def get_bamboo_result(uri):
    try:
        response = requests.get(uri, verify=False, proxies=proxies)
        return json.loads(response.text)["successful"]
    except Exception as e:
        log.error("Can't get info from Bamboo:\n{0}".format(e))
        return None


def collect_bamboo_data():
    results = {}
    for env in ci_environments:
        env_results = {}
        for project, ci_tag in ci_environments[env].items():
            uri = conf['bamboo']['uri'].format(tag=ci_tag)
            env_results.update({project: get_bamboo_result(uri)})
            logger.info("env: {1} tag: {2} success: {3}"
                  .format(project, ci_tag, env_results))
        results[env] = env_results
    return results

# TODO: add last downtime facility for Geckoboard
