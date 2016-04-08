from logger import logger
import re
from time import strptime
from mcmaster_utils import stash
import datetime


class Merge:
    """
    check for unmerged branches
    """

    def __init__(self, settings):
        self.settings = settings

    def poll(self):
        self.refresh_repos()
        unmerged_branches = []
        for repo in self.settings['repos']:
            for branch in self.branches(repo):
                if not self.merged(branch):
                    unmerged_branches.append(branch)

    def merged(self, branch, master):
        if self.fits(branch):
            return self.tim_merge_check(branch, master)
        else:
            return True

    def tim_merge_check(self, branch, master):
        gitClient = GitClient('../scratch/integration-services')
        for branch in gitClient.getFilteredRemoteBranchList():
            branchChangeset = gitClient.getBranchLatestChangeset(branch)
            #resultList = ["%s: [%s]" % (branch, branchChangeset)]
            resultList = ["%s" % (branch)]
            for refBranch in refBranches:
                refBranchChangeset = gitClient.getBranchLatestChangeset(refBranch)
                sharedChangeset = gitClient.getSharedChangeset(branch,refBranch)
                #merged = ("Merged" if (branchChangeset == sharedChangeset[0].hexsha) else "Not Merged")
                #result = "[%s=%s|%s]" % (branchChangeset, sharedChangeset[0].hexsha,(branchChangeset == sharedChangeset[0].hexsha))
                result = "Merged" if (branchChangeset == sharedChangeset[0].hexsha) else "Not Merged"
                resultList.append("%s" % result)
            print(",".join(resultList))

    def branches(self, repo):
        pass

    def refresh_repos(self):
        for repo in self.settings['repos']:
            self.gitfetchall(repo)

    def gitfetchall(self, repo):
        pass

    def fits(self, branch):
        in_date_range = branch.created > strptime(self.settings['start'], '%d/%m/%y')
        old = branch.created < datetime.date.today() - self.settings['max_days']
        branch_name_matches = any(re.match(pattern, branch) for pattern in self.settings['name_patterns'])
        return in_date_range and old and branch_name_matches
