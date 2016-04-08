#!flask/Scripts/python

from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client

class Neo4jAdapter(object):
	def __init__(self):
		#self.db = GraphDatabase("http://localhost:7474", username="neo4j", password="EverythingIsConnected")
		self.db = GraphDatabase("http://localhost:7474")

	def query(self, q):
		results = self.db.query(q, returns=(client.Node))
		return results

	def createNode(self, **props):
		return self.db.nodes.create(**props)

	def createLabel(self, name):
		return self.db.labels.create(name)

	def createRelationship(self, n1, n2, linkType, **props):
		n1.relationships.create(linkType, n2, **props)

