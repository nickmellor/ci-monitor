#!flask/Scripts/python

from .rest import RestClient


class StashAdapter(object):
    def __init__(self, project, repo):
        self.project = project
        self.repo = repo
        self.rest = RestClient("stash", "https://stash.aws.medibank.local/rest/api/1.0/projects")
        self.commitIndex = {}

    def getCommitFromStash(self, cid):
        data = self.rest.get(200, "/%s/repos/%s/commits/%s" % (self.project, self.repo, cid))
        jira = data["properties"]["jira-key"][0]
        message = data["message"]
        return Commit(cid, jira, message)

    def getCommit(self, cid):
        if cid in self.commitIndex:
            return self.commitIndex[cid]
        commit = self.getCommitFromStash(cid)
        self.commitIndex[cid] = commit
        return commit

    def getBranchCommits(self, prevBranch, branch):
        return self.getCommits(prevBranch.latestCommit, branch.latestCommit)

    def getCommits(self, since, until):
        data = self.rest.get(200, "/%s/repos/%s/commits/?since=%s&until=%s" % (self.project, self.repo, since, until))
        values = data["values"]
        commits = []
        for value in values:
            cid = value["id"]
            jira = value["attributes"]["jira-key"] if "attributes" in value else None
            name = value["author"]["displayName"] if "author" in value and "displayName" in value["author"] else None
            email = value["author"]["emailAddress"] if "author" in value else None
            message = value["message"]
            commit = Commit(cid, jira, message, name, email)
            commits.append(commit)
        return commits

    def getFiles(self, changeset):
        data = self.rest.get(200, "/%s/repos/%s/commits/%s/changes?start=0&limit=1000" % (
        self.project, self.repo, changeset))
        values = data["values"]
        files = []
        for value in values:
            file = value["path"]["toString"]
            files.append(file)
        return files

    def getBranches(self):
        return [branch for branch in self._getBranchesGenerator()]

    def getBranch(self, name):
        return [branch for branch in self._getBranchesGenerator() if branch.displayId == name][0]

    def getReleaseBranches(self):
        return [branch for branch in self._getBranchesGenerator() if
                (branch.displayId.startswith("release/") or branch.displayId.startswith("hotfix/"))]

    def _getBranchesGenerator(self):
        data = self.rest.get(200, "/%s/repos/%s/branches?limit=500" % (self.project, self.repo))
        values = data["values"]
        for value in values:
            displayId = value["displayId"]
            refId = value["id"]
            latestCommit = value["latestCommit"]
            yield Branch(displayId, refId, latestCommit)

        # def _getCommitsGenerator(self, max):


class Commit(object):
    def __init__(self, id, jira, message, name, email):
        self.id = id
        self.jira = jira
        self.name = name
        self.email = email
        self.message = message

    def __repr__(self):
        return "Commit(ID:%s | JIRA:%s | Author:%s(%s)\n\tMessage:%s)" % (
        self.id, self.jira, self.name, self.email, self.message)


class Branch(object):
    def __init__(self, displayId, refId, latestCommit):
        self.displayId = displayId
        self.refId = refId
        self.latestCommit = latestCommit

    def __repr__(self):
        return "Branch(DisplayID:%s, RefId:%s, LatestCommit:%s)" % (self.displayId, self.refId, self.latestCommit)
