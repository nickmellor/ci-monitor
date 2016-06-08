import datetime
import os
import re

import yaml

from mcmaster_utils import gitclient
from monitor import Monitor
from utils.logger import logger


class Merge(Monitor):
    """
    check stash/git repo for revisions not merged back into base branch
    """

    def __init__(self, indicator, monitor_class, settings):
        super().__init__(monitor_class)
        self.indicator = indicator
        self.settings = settings
        self.name = self.settings.name
        self.projects = [gitclient.GitClient(os.path.join(self.settings['location'], project))
                       for project
                       in settings['repos']]
        self.errors = set()
        self.old_errors = set()

    def poll(self):
        # self.refresh_projects()
        self.old_errors = self.errors
        self.errors = set()
        master_branch_name = self.settings.master
        for project in self.projects:
            project_name = project.repo._working_tree_dir.split(os.path.sep)[-1]
            logger.info("{indicator}: reconciling master branch merges in project '{project}'"
                .format(indicator=self.indicator, project=project_name))
            # project.repo.remotes.origin.fetch() -- has timeout at present
            deploy_rev = latest_commit(project, master_branch_name).hexsha
            for branch in self.branches(project):
                release_rev = latest_commit(project, branch).hexsha
                if not project.repo.is_ancestor(release_rev, deploy_rev):
                    error = "{indicator}: unmerged in project '{project}': {branch} -> {destination}"\
                            .format(indicator=self.indicator, project=project_name,
                                    branch=branch, destination=master_branch_name)
                    if error not in self.old_errors:
                        logger.error(error)
                    self.errors.add(error)

    def tests_ok(self):
        return not self.errors

    def comms_ok(self):
        # TODO: comms error if can't git clone
        return True

    def has_changed(self):
        return self.old_errors != self.errors

    def branches(self, project):
        branches_and_merges = (tidy_branch(branch) for branch in project.remote_branches(project.repo))
        yield from (branch_or_merge for branch_or_merge in branches_and_merges
                    if not is_merge(branch_or_merge) and self.fits_criteria(project, branch_or_merge))

    def refresh_projects(self):
        # self.clear_repos(self.repo_dir())
        for name, url in self.settings['repos'].items():
            logger.info("cloning project '{0}'".format(name))
            old_cwd = os.getcwd()
            os.chdir(self.repo_dir())
            os.system('git clone {0}'.format(url))
            os.chdir(old_cwd)

    def repo_dir(self):
        return os.path.normpath(self.settings['location'])

    def clear_repos(self, top_level_dir):
        # TODO: maybe this will fix the problem of git repos not being completely removed
        # from subprocess import Popen, PIPE, STDOUT
        #
        # cmd = 'rm -frv /path/to/dir'
        # p   = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        # out = p.stdout.read()
        # print(out)
        for root, dirs, files in os.walk(top_level_dir, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except:
                    pass
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except:
                    pass

    def fits_criteria(self, project, branch):
        commit_date = self.last_commit_date(project, branch)
        too_old = commit_date < datetime.datetime.now() - datetime.timedelta(weeks=self.settings.max_age_weeks)
        is_stale = commit_date < datetime.datetime.now() - datetime.timedelta(days=self.settings.stale_days)
        branch_name_matches = any(re.match(pattern, branch)
                                  for pattern
                                  in self.settings['name_patterns'])
        return is_stale and branch_name_matches and not too_old

    def last_commit_date(self, project, branch):
        return datetime.datetime.fromtimestamp(latest_commit(project, branch).committed_date)

    def comms_error(self):
        return False

def is_merge(branch):
    return '->' in branch


def tidy_branch(branch):
    return branch[2:] if branch.startswith('*') else branch


def latest_commit(project, branch):
    revision = project.latest_changeset(tidy_branch(branch))
    return project.repo.commit(revision)