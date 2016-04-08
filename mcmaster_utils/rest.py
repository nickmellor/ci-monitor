#!flask/Scripts/python

import urllib3
import json
import requests
from .auth import AuthClient

http = urllib3.PoolManager()
urllib3.disable_warnings()


class RestClient(object):
    def __init__(self, component, base):
        self.base = base
        self.auth = AuthClient(component)

    def get(self, expectedStatus=200, path=""):
        response = self.getRAW(expectedStatus, path)
        data = json.loads(response)
        return data

    def post(self, expectedStatus=200, path="", body={}):
        response = self.postRAW(expectedStatus, path, body)
        data = json.loads(response)
        return data

    def postRAW(self, expectedStatus=200, path="", body={}):
        headers = self.auth.createHeader()
        headers["Content-Type"] = "application/json"
        url = self.base + path
        # print("URL: " + url)
        bodyString = json.dumps(body)
        # print("BODY: " + bodyString)
        response = http.request(method="POST", url=url, body=bodyString, headers=headers)
        # print(response)
        if response.status != expectedStatus:
            raise Exception("Problem while posting: " + repr(response.status))
        data = response.data.decode("utf-8")
        # print(data)
        return data

    def getRAW(self, expectedStatus=200, path=""):
        headers = self.auth.createHeader()
        url = self.base + path
        # print("URL: " + url)
        response = http.request("GET", url, {}, headers)
        if response.status != expectedStatus:
            raise Exception("Problem while posting: " + repr(response.status))
        data = response.data.decode("utf-8")
        # print(data)
        return data
