from conf import conf
from proxies import proxies
import requests
import xml.etree.ElementTree as ET
import json
from logger import logger

interesting = conf['bsm']['interesting']

okstatus = conf['bsm']['okstatus']

def bsm_results():
    faults = set()
    bsm_response = get_bsm_data()
    tree = ET.parse(bsm_response)
    root = tree.getroot()
    for node in root.iter('node'):
        for resource in node.iter("dimension"):
            bsm_feedback = resource.attrib
            if bsm_feedback['name'] == 'Software Availability' and bsm_feedback['status'] not in okstatus:
                faults.add(node.attrib['name'])
                print(node.attrib['name'], bsm_feedback['status'])
    print('\n\n')
    print('\n'.join(sorted(list(faults))))


def get_bsm_data():
    try:
        uri = conf['bsm']['uri']
        response = requests.get(uri, verify=False, proxies=proxies)
        return json.loads(response.text)["successful"]
    except Exception as e:
        logger.error("Can't get info from Bamboo:\n{0}".format(e))
        return None

