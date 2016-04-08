#!flask/Scripts/python

import urllib3
import json

http = urllib3.PoolManager()
urllib3.disable_warnings()

host = "localhost"
port = "port"
listPath = "list"

# set JAVA_OPTS=-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=8855 -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false
# https://jolokia.org/reference/html/protocol.html#read
# http://localhost:8080/jolokia/list

class JMXAdapter(object):
	def __init__(self, headers):
		self.headers = headers
		self.configIndex = {}

	def getConfigFromJMX(self, path):
		response = http.request("GET", "http://%s:%s/%s" % (host,port,path), {}, self.headers)
		data = json.loads(response.data.decode("utf-8"))
		value = 42
		return Commit(path, value)

	def getCommit(self, cid):
		if path in self.configIndex:
			return self.commitIndex[cid]
		commit = self.getCommitFromStash(cid)
		self.commitIndex[cid] = commit
		return commit

class Config(object):
	def __init__(self, path, value):
		self.path = path
		self.value = value
