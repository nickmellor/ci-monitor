#!/usr/bin/python3.4

# from urllib3 import PoolManager
# import urllib3

from lxml import html
from .rest import RestClient
import json
import sys


# from auth import AuthClient

# http = urllib3.PoolManager()
# urllib3.disable_warnings()

# auth = AuthClient("graylog")
# headers = auth.createHeader()
# url = "https://graylog.aws.medibank.local/search?fields=message,source&width=1583&rangetype=relative&relative=300&q=((source:aem-pub-l-prod01-prod.digi-aws.medibank.local%20AND%20NOT%20tag:fluent.*%20AND%20NOT%20tag:newrelic.*%20AND%20NOT%20tag:cq5.dispatcher%20AND%20NOT%20tag:system.syslog.*%20AND%20NOT%20tag:cq5.u01.cq5.publish.crx-quickstart.logs.*%20AND%20NOT%20message:%22GET%20/etc/designs/static-style/clientlibs*%22)%20OR%20(source:svc-api-l-prod01-prod.digi-aws.medibank.local%20AND%20NOT%20tag:system.syslog.*%20AND%20NOT%20tag:fluent.*)%20OR%20(source:svc-int-l-prod01-prod.digi-aws.medibank.local%20AND%20NOT%20tag:system.syslog.*))#fields=message%2Csource"
# response = http.request("GET", url, {}, headers)
# result = response.data.decode("utf-8")
# #fh = open("graylog-html-results.html")
# #result = fh.read()
# doc = html.fromstring(result)
# value = doc.xpath("//div[@id="react-search-result"]/@data-search-result")[0]
# value = value.replace("&quotquot;", """)
# value = value.replace("&quot;", """)
# print(value)

debug = False

class GraylogClient(object):
	def __init__(self):
		self.rest = RestClient("graylog", "https://graylog.aws.medibank.local/search?")
		try:
			# this is here as a temprary bugfix, because Graylog first login seams to always fail
		   	self.search('rangetype=relative&fields=message%2Csource&width=1583&relative=1')
		except:
			if debug:
				print('WARN: Logging into Graylog failed. Going to retry.');

	def search(self, searchURL):
		result = self.rest.getRAW(200, searchURL)
		doc = html.fromstring(result)
		value = doc.xpath('//div[@id="react-search-result"]/@data-search-result')[0]
		value = value.replace("&quotquot;", """)
		value = value.replace("&quot;", """)
		#print(value)
		data = json.loads(value)
		#print(data)
		return data

class Result(object):
	def __init__(self, timestamp):
		self.timestamp = timestamp