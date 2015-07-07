import xml.etree.ElementTree as ET
tree = ET.parse('bsm_example.xml')
root = tree.getroot()

interesting = ['AWS/AEM',
               'Customer Loyality',  # sic
                'OMS', 'Sales Site']

ok_statuses = ['20']

def nodeget():
    faults = set()
    for node in root.iter('node'):
        for machine in node.iter("dimension"):
            mattr = machine.attrib
            if mattr['name'] == 'Software Availability' and mattr['status'] not in ok_statuses:
                faults.add(node.attrib['name'])
                print(node.attrib['name'], mattr['status'])
    print('\n\n')
    print('\n'.join(sorted(list(faults))))


nodeget()
