#!/usr/bin/python3.4

import sys
sys.path.insert(0, "../libs")

from .auth import AuthClient

import urllib3
import json


http = urllib3.PoolManager()
urllib3.disable_warnings()

BASE_URL = "https://bamboo.digidev-aws.medibank.local/rest/api"
GET_LATEST_URL = "%s/latest/result/%s/latest.json"


class BambooClient(object):
    headers = {}

    def __init__(self):
        auth = AuthClient('bamboo')  # will default to admin:admin
        #self.headers = auth.createHeader()

    def _getPlanStatusListGenerator(self, jobs):
        for job in jobs:
            url = GET_LATEST_URL % (BASE_URL, job)
            print("URL: " + url)
            #print("Headers: " + self.headers['Authorization'])
            response = http.request("GET", url, {}, self.headers)
            data = json.loads(response.data.decode("utf-8"))
            print("Data: " + repr(data))
            if "status-code" in data:
                print("There was a problem: Status(%s)" % (data["status-code"]) )
            else:
                planKey = job
                planName = data["planName"]
                completionDate = data["buildCompletedDate"]
                status = data["buildState"]
                yield BambooPlan(planKey, planName, completionDate, status)

    def getPlanStatusList(self, jobs):
        return [plan for plan in self._getPlanStatusListGenerator(jobs)]

class BambooPlan(object):
    def __init__(self, planKey, planName, completionDate, status):
        self.planKey = planKey
        self.planName = planName
        self.completionDate = completionDate
        self.status = status

    def __repr__(self):
        return "BambooPlan(PlanKey:%s, PlanName:%s, CompletionDate:%s, State:%s)" % (self.planKey, self.planName, self.completionDate, self.status)

