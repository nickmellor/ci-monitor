import datetime
import errno
import os
import re
import sys
import tempfile
from subprocess import Popen, PIPE

from listener import Listener
from utils import gitclient
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

    @staticmethod
    def make_sure_dir_exists(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def poll(self):
        self.clone_project()
        project_name = self.project.repo._working_tree_dir.split(os.path.sep)[-1]
        self.old_errors = self.errors
        self.errors = set()
        master_branch = self.settings['master']
        logger.info("{indicator}: reconciling master branch merges in project '{project}'"
                    .format(indicator=self.indicator_name, project=project_name))
        for branch in self.branch_candidates():
            self.check_merge_status(branch, master_branch, project_name)
        self.delete_directory(self.clone_location)

    def check_merge_status(self, branch, master_branch, project_name):
        master_rev = self.latest_commit(master_branch).hexsha
        release_rev = self.latest_commit(branch).hexsha
        if not self.project.repo.is_ancestor(release_rev, master_rev):
            self.record_unmerged_branch(branch, master_branch, project_name)

    def record_unmerged_branch(self, branch, master_branch, project_name):
        error = "{indicator} ({listener}): unmerged branch in repo " \
                "'{project}': {branch} -> {destination} last revision {age} days old" \
            .format(indicator=self.indicator_name, listener=self.name, project=project_name,
                    branch=branch, destination=master_branch,
                    date=self.last_commit_date(branch),
                    age=self.days_since_last_revision(branch))
        if error not in self.old_errors:
            logger.error(error)
        self.errors.add(error)

    def latest_commit(self, branch):
        revision = self.project.latest_changeset(tidy_branch(branch))
        return self.project.repo.commit(revision)

    def tests_ok(self):
        return not self.errors

    def comms_ok(self):
        # TODO: comms error if can't git clone
        return True

    def has_changed(self):
        return self.old_errors != self.errors

    def branch_candidates(self):
        branches_and_merges = (tidy_branch(branch) for branch in self.project.remote_branches(self.project.repo))
        branches = (branch_or_merge for branch_or_merge in branches_and_merges
                    if not is_merge(branch_or_merge))
        yield from (branch for branch in branches if self.fits_criteria(branch))

    def clone_project(self):
        # self.clone_location = r'scratch\repos'
        self.clone_location = tempfile.mkdtemp(prefix='cim_merge_')
        name = self.settings['name']
        url = self.settings['repo']
        logger.info("cloning project '{project}' in directory {location}".format(project=name, location=self.clone_location))
        repo_path = os.path.join(self.clone_location,
                                 self.project_dirname(self.settings['repo']))
        cmd = 'git clone {url} {repo}'.format(url=url, repo=repo_path)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=not sys.platform.startswith("win")).communicate()
        self.project = gitclient.GitClient(repo_path)

    def project_dirname(self, git_url):
        return os.path.splitext(os.path.basename(git_url))[0]

    def repo_dir(self):
        return os.path.normpath(self.clone_location)

    def delete_directory(self, root_dir):
        # NB present implementation does not clear the clone temporary directory due to script permissions
        # temporary directories will need clearing manually or via an enabled script
        pass

    def fits_criteria(self, branch):
        return self.fits_name_criteria(branch) and self.fits_age_criteria(branch)

    def fits_name_criteria(self, branch):
        name_selected = any(re.match(pattern, branch) for pattern in self.settings['name_patterns'])
        whitelist = self.settings.get('whitelist')
        if whitelist:
            regex_match = any(re.match(pattern, branch) for pattern in whitelist)
            substring_match = any(substring in branch for substring in whitelist)
            whitelisted = regex_match or substring_match
        else:
            whitelisted = False
        return name_selected and not whitelisted

    def fits_age_criteria(self, branch):
        age_days = self.days_since_last_revision(branch)
        too_old = age_days > self.settings['max_age_weeks'] * 7
        is_stale = age_days > self.settings['stale_days']
        return is_stale and not too_old

    def days_since_last_revision(self, branch):
        return (datetime.datetime.now() - self.last_commit_date(branch)).days

    def last_commit_date(self, branch):
        return datetime.datetime.fromtimestamp(self.latest_commit(branch).committed_date)

    def comms_error(self):
        return False


def is_merge(branch):
    return '->' in branch


def tidy_branch(branch):
    return branch[2:] if branch.startswith('*') else branch