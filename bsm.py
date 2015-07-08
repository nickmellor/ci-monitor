from conf import conf
import xml.etree.ElementTree as ET
tree = ET.parse('bsm_example.xml')
root = tree.getroot()

interesting = conf['bsm']['interesting']

okstatus = conf['bsm']['okstatus']

def nodeget():
    faults = set()
    for node in root.iter('node'):
        for resource in node.iter("dimension"):
            bsm_feedback = resource.attrib
            if bsm_feedback['name'] == 'Software Availability' and bsm_feedback['status'] not in okstatus:
                faults.add(node.attrib['name'])
                print(node.attrib['name'], bsm_feedback['status'])
    print('\n\n')
    print('\n'.join(sorted(list(faults))))


nodeget()
