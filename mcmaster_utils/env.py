#!flask/Scripts/python

import urllib3
import json

http = urllib3.PoolManager()
urllib3.disable_warnings()


#
#  Manages the interactions with JIRA
#

class EnvClient(object):
    def __init__(self, headers):
        self.headers = headers

    def getEnv(self, service, keys):
        url = "https://integration-dev01-nprd.digidev-aws.medibank.local/%s/actuator/env" % (service)
        # print('dsfsdfsdf: ' + self.headers['Authorization'])
        response = http.request("GET", url, {}, self.headers)
        # print('Response: ' + repr(response))
        data = json.loads(response.data.decode("utf-8"))
        # print('Data: ' + repr(data))
        env = {}
        for key in keys:
            for setName in data:
                if key in data[setName]:
                    env[key] = data[setName][key]
                    break

        return EnvConfig(service, env)


#
#  Represents a JIRA ticket
#

class EnvConfig(object):
    def __init__(self, service, env):
        self.service = service
        self.env = env
