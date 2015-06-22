import datetime
from proxies import proxies
import requests
import json

ci_environments = {
    'DEV': {
        "Smoke": "MEDIBANKCORP-RCWAT",
        "Retail": "MEDIBANKCORP-RCWAT3",
        "Corp": "MEDIBANKCORP-RCWAT0",
        "Elevate": "MEDIBANKCORP-RCWAT17",
        "Inc": "MEDIBANKCORP-RCWAT21",
    },
    'TEST': {
        "Corporate": "MEDIBANKCORP-RCWAT9",
        "Elevate": "MEDIBANKCORP-RCWAT18",
        "Inc": "MEDIBANKCORP-RCWAT22",
        "Retail": "MEDIBANKCORP-RCWAT8"

    },
    'SIT': {
        "Retail": "MEDIBANKCORP-RCWAT4",
        "Corp": "MEDIBANKCORP-RCWAT5",
        "Inc": "MEDIBANKCORP-RCWAT23",
        "Elevate": "MEDIBANKCORP-RCWAT19"
    }
}

def get_bamboo_result(uri):
    try:
        response = requests.get(uri, verify=False, proxies=proxies)
        return json.loads(response.text)["successful"]
    except Exception as e:
        print("ERROR: can't get info from Bamboo:\n{0}".format(e))
        return None


def collect_bamboo_data():
    results = {}
    for env in ci_environments:
        env_results = {}
        for project, ci_tag in ci_environments[env].items():
            uri = "https://bamboo-corp.dev.medibank.com.au/rest/api/latest/result/{tag}/latest.json".format(tag=ci_tag)
            env_results.update({project: get_bamboo_result(uri)})
            print("{0} env: {1} tag: {2} success: {3}"
                  .format(datetime.datetime.now(), project, ci_tag, env_results))
        results[env] = env_results
    return results

# TODO: add last downtime facility for Geckoboard
