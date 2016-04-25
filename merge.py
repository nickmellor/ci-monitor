from logger import logger
import re
import os
import time
from mcmaster_utils import gitclient
import datetime
import yaml
from git import Repo


class Merge:
    """
    check stash/git branches for
    """

    def __init__(self, settings):
        self.settings = settings
        self.projects = [gitclient.GitClient(os.path.join(self.settings['location'], project))
                       for project
                       in settings['repos']]

    def poll(self):
        self.refresh_projects()
        unmerged_branches = []
        for deploy_branch_name in ['develop']:
            for project in self.projects:
                # project.repo.remotes.origin.fetch() -- has timeout at present
                deploy_branch = project.repo.commit(deploy_branch_name)
                for branch in self.branches(project):
                    release_branch = project.repo.commit(branch.name).hexsha
                    if not project.repo.is_ancestor(release_branch, deploy_branch):
                        unmerged_branches.append(branch.name)
        print(unmerged_branches)

    def merged(self, project, branch, master):
        branch_changeset = project.latest_changeset(branch)
        shared_changeset = project.shared_changeset(branch, master)
        return branch_changeset == shared_changeset[0].hexsha

    def branches(self, project):
        yield from (branch for branch in project.remote_branches(project.repo) if self.fits_criteria(branch))

    def refresh_projects(self):
        for project in self.settings['repos']:
            self.gitfetchall(project)

    def gitfetchall(self, project):
        # location config
        pass

    def fits_criteria(self, branch):
        commit_date = datetime.datetime.fromtimestamp(branch.commit.committed_date)
        too_old_to_bother = commit_date < datetime.datetime.strptime(self.settings['start'], '%d/%m/%Y')
        stale = commit_date < datetime.datetime.now() - datetime.timedelta(days=self.settings['max_days'])
        branch_name_matches = any(re.match(pattern, branch.name)
                                  for pattern
                                  in self.settings['name_patterns'])
        return True
        # return stale and branch_name_matches and not too_old_to_bother


if __name__ == '__main__':
    with open('conf.yaml') as config_file:
        settings = yaml.load(config_file)['signallers']['MERGETEST']['merge']
    m = Merge(settings)
    m.poll()
    # repo = Repo('scratch/repos/integration-services')
    # d = repo.heads['develop'].commit.committed_date
    # print(time.gmtime(d))
