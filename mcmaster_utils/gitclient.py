#!/usr/bin/python3.4

from git import Repo


class GitClient(object):
    def __init__(self, repoPath):
        self.repo = Repo(repoPath)
        assert not self.repo.bare

    def getSharedChangeset(self, ref1, ref2):
        return self.repo.merge_base(ref1, ref2)

    def getFilteredRemoteBranchList(self):
        git = self.repo.git
        branchList = [branch.strip() for branch in git.branch('--list', '-a').split('\n')]
        return [branch for branch in branchList if self.isInteresting(branch)]

    def isInteresting(self, branch):
        return (branch == 'remotes/origin/master' or branch == 'remotes/origin/develop'
                or branch.startswith("remotes/origin/release/") or branch.startswith("remotes/origin/hotfix/"))

    def getBranchLatestChangeset(self, branch):
        git = self.repo.git
        changeset = git.log('-n', '1', '--pretty=format:"%H"', branch)
        return changeset.strip('"')
