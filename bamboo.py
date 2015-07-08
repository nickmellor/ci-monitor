from logger import logger
from conf import conf
from proxies import proxies
import requests
import json

ci_environments = conf['bamboo']['environments']

def get_bamboo_result(uri):
    try:
        response = requests.get(uri, verify=False, proxies=proxies)
        return json.loads(response.text)["successful"]
    except Exception as e:
        logger.error("Can't get info from Bamboo:\n{0}".format(e))
        return None


def collect_bamboo_data():
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
