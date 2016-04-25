#!/usr/bin/python3.4

from git import Repo


class GitClient(object):
    def __init__(self, repoPath):
        self.repo = Repo(repoPath)
        assert not self.repo.bare

    def shared_changeset(self, ref1, ref2):
        return self.repo.merge_base(ref1, ref2)

    def remote_branches(self, repo):
        git = self.repo.git
        return [branch.strip() for branch in git.branch('--list', '-a').split('\n')]

    def latest_changeset(self, branch):
        git = self.repo.git
        changeset = git.log('-n', '1', '--pretty=format:"%H"', branch)
        return changeset.strip('"')
