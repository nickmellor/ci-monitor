#!flask/Scripts/python

import base64
from os.path import expanduser


class AuthClient(object):
    def __init__(self, client):
        self.client = client

    def _loadConfig(self):
        configfile = "%s/.caconfig" % (expanduser('~'));
        return dict(line.strip().split("=")
                    for line in open(configfile)
                    if not line.strip().startswith("#"))

    def createHeader(self):
        headers = {}
        self.addAuth(headers)
        return headers

    def addAuth(self, headers):
        config = self._loadConfig()
        authEnv = config[self.client] if self.client in config else "admin:admin"
        authEnvBase64 = base64.b64encode(authEnv.encode("utf-8")).decode("ascii")
        # print("Auth %s" % (authEnv))
        # print("Basic %s" % (authEnvBase64))
        headers["Authorization"] = "Basic %s" % (authEnvBase64)
