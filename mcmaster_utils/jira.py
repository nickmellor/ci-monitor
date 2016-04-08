#!flask/Scripts/python

from rest import RestClient

#
#  Manages the interactions with JIRA
#
#  Get a list of views (New OMS is 143): 
#  https://jira.aws.medibank.local/rest/greenhopper/1.0/rapidviews/viewsData
#

class JiraClient(object):

    def __init__(self):
        self.epicIndex = {}
        self.storyIndex = {}
        self.rest = RestClient("jira", "https://jira.aws.medibank.local/rest/api/latest")

    def _dataToTicket(self, data):
        type = data["fields"]["issuetype"]["name"]
        epic = data["fields"]["customfield_10006"]
        id = data["id"]
        key = data["key"]
        summary = data["fields"]["summary"]
        description = data["fields"]["description"]
        fixVersions = [fix["name"] for fix in data["fields"]["fixVersions"]]
        return Ticket(id, key, type, epic, summary, description, fixVersions)

    def _resultToTicketRef(self, result):
        key = result['key']
        summary = result.get('fields', {}).get('summary')
        return TicketRef(key, summary)

    def getTicketFromJira(self, dssid):
        data = self.rest.get(expectedStatus=200, path="/issue/"+dssid)
        return self._dataToTicket(data)

    def getTicket(self, dssid):
        if dssid in self.storyIndex:
            return self.storyIndex[dssid]
        elif dssid in self.epicIndex:
            return self.epicIndex[dssid]

        ticket = self.getTicketFromJira(dssid)

        if ticket.type == "Story":
            self.storyIndex[dssid] = ticket
        elif ticket.type == "Epic":
            self.epicIndex[dssid] = ticket

        return ticket

    def getReleases(self):
        data = self.rest.get(expectedStatus=200, path="/project/DSS/versions")
        for result in data:
            release = self._resultToRelease(result)
            if release.archived == False:
                yield release

    def _resultToRelease(self, result):
        name = result["name"]
        archived = result["archived"]
        rid = result["id"]
        return Release(rid, name, archived)

    def getReleaseTickets(self, projectId, releaseId):
        searchString = "project = %s AND fixVersion = %s ORDER BY priority DESC, key ASC" % (projectId, releaseId)
        searchQuery = {"jql":searchString,"maxResults":1000,"fields":["id", "summary"]}
        data = self.rest.post(expectedStatus=200, path="/search", body=searchQuery)
        for result in data['issues']:
            ticketRef = self._resultToTicketRef(result)
            yield ticketRef

#
#  Represents a JIRA ticket
#

class TicketRef(object):
    def __init__(self, key, summary):
        self.key = key
        self.summary = summary
    def __repr__(self):
        return "TicketRef(Key(%s), Summary(%s))" % (self.key, self.summary)

class Release(object):
    def __init__(self, rid, name, archived):
        self.name = name
        self.archived = archived
        self.id = rid

    def __repr__(self):
        return "Release(Id(%s),Name(%s),Archived(%s))" % (self.id, self.name, self.archived)


class Ticket(object):
    def __init__(self, id, key, type, epic, summary, description, fixVersions):
        self.id = id
        self.key = key
        self.type = type
        self.epic = epic
        self.summary = summary
        self.description = description
        self.fixVersions = fixVersions
        self.children = set()
        self.parents = set()
