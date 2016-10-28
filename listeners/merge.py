import datetime
import errno
import os
import re
import shutil
import sys
from subprocess import Popen, PIPE
import tempfile

from listener import Listener
from mcmaster_utils import gitclient
from utils.filehandling import clear_dir
from utils.logger import logger


class Merge(Listener):
    """
    check stash/git repo for branches not merged back into base branch
    e.g. ensure all hotfix branches are merged back into master
    There is a cut-off age for time of last commit beyond which Merge will
    no longer complain
    """

    def __init__(self, indicator_name, listener_class, settings):
        super().__init__(indicator_name, listener_class, settings)
        self.errors = set()
        self.old_errors = set()
        self.settings = settings

    def project_dirname(self, git_url):
        return os.path.splitext(os.path.basename(git_url))[0]

    @staticmethod
    def make_sure_dir_exists(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def poll(self):
        self.clone_location = r'scratch\repos'
        self.refresh_project()
        project_name = self.project.repo._working_tree_dir.split(os.path.sep)[-1]
        self.old_errors = self.errors
        self.errors = set()
        master_branch_name = self.settings['master']
        logger.info("{indicator}: reconciling master branch merges in project '{project}'"
                    .format(indicator=self.indicator_name, project=project_name))
        master_rev = latest_commit(self.project, master_branch_name).hexsha
        for branch in self.branches(self.project):
            release_rev = latest_commit(self.project, branch).hexsha
            if not self.project.repo.is_ancestor(release_rev, master_rev):
                error = "{indicator} ({listener}): unmerged branch in repo " \
                        "'{project}': {branch} -> {destination} last revision dated {date}" \
                    .format(indicator=self.indicator_name, listener=self.name, project=project_name,
                            branch=branch, destination=master_branch_name,
                            date=self.last_commit_date(self.project, branch))
                if error not in self.old_errors:
                    logger.error(error)
                self.errors.add(error)
        self.clear_repo()

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

    def refresh_project(self):
        self.clear_repo(self.repo_dir())
        name = self.settings['name']
        url = self.settings['repo']
        logger.info("cloning project '{0}'".format(name))
        repo_path = os.path.join(self.clone_location,
                                 self.project_dirname(self.settings['repo']))
        repo_root = os.path.join(repo_path, os.path.splitext(url.split('/')[-1])[0])
        cmd = 'git clone {0} {1}'.format(url, repo_path)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=not sys.platform.startswith("win")).communicate()
        # os.system('git clone {0}'.format(url))
        self.project = gitclient.GitClient(repo_path)

    def repo_dir(self):
        return os.path.normpath(self.clone_location)

    def clear_repo(self, root_dir):
        # clear_dir(root_dir)
        # shutil.rmtree(root_dir)
        # # TODO: Nick Mellor 26/08/2016: maybe this will fix the problem of git repos not being completely removed
        # cmd = 'rm -frv {dir}'.format(dir=top_level_dir)
        # p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=not sys.platform.startswith("win")).communicate()
        ##### currently not responsible for deleting clone #####
        # NB present implementation does not clear the clone temporary directory due to script permissions
        # temporary directories will need clearing manually or via an enabled script
        pass

    def fits_criteria(self, project, branch):
        commit_date = self.last_commit_date(project, branch)
        too_old_to_bother_with = commit_date < datetime.datetime.now() - datetime.timedelta(weeks=self.settings['max_age_weeks'])
        branch_is_stale = commit_date < datetime.datetime.now() - datetime.timedelta(days=self.settings['stale_days'])
        branch_name_fits_pattern = any(re.match(pattern, branch)
                                  for pattern
                                  in self.settings['name_patterns'])
        return branch_is_stale and branch_name_fits_pattern and not too_old_to_bother_with

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
