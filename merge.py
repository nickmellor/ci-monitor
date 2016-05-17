from infrastructure import Infrastructure
from logger import logger
import re
import os
from mcmaster_utils import gitclient
import datetime
import yaml


class Merge(Infrastructure):
    """
    check stash/git branches for
    """

    def __init__(self, indicator, settings):
        self.indicator = indicator
        self.settings = settings
        self.name = self.settings.name
        self.projects = [gitclient.GitClient(os.path.join(self.settings['location'], project))
                       for project
                       in settings['repos']]

    def poll(self):
        # self.refresh_projects()
        unmerged_branches = []
        for deploy_branch_name in self.settings.deployments:
            for project in self.projects:
                logger.info("{indicator}: reconciling master branches in project '{0}'".format(self.indicator,
                    project.repo._working_tree_dir.split(os.path.sep)[-1]))
                # project.repo.remotes.origin.fetch() -- has timeout at present
                deploy_rev = latest_commit(project, deploy_branch_name).hexsha
                for branch in self.branches(project):
                    # logger.info('Processing branch {0}'.format(branch))
                    release_rev = latest_commit(project, branch).hexsha
                    if not project.repo.is_ancestor(release_rev, deploy_rev):
                        unmerged_branches.append((project.repo._working_tree_dir.split(os.path.sep)[-1], branch))
        print(unmerged_branches)

    def branches(self, project):
        branches_and_merges = (tidy_branch(branch) for branch in project.remote_branches(project.repo))
        yield from (branch_or_merge for branch_or_merge in project.remote_branches(project.repo)
                    if not is_merge(branch_or_merge) and self.fits_criteria(project, branch_or_merge))

    def refresh_projects(self):
        self.clear_repos(self.repo_dir())
        for name, url in self.settings['repos'].items():
            logger.info("cloning project '{0}'".format(name))
            old_cwd = os.getcwd()
            os.chdir(self.repo_dir())
            os.system('git clone {0}'.format(url))
            os.chdir(old_cwd)

    def repo_dir(self):
        return os.path.normpath(self.settings['location'])

    def clear_repos(self, top_level_dir):
        for root, dirs, files in os.walk(top_level_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def fits_criteria(self, project, branch):
        commit = latest_commit(project, branch)
        commit_date = datetime.datetime.fromtimestamp(commit.committed_date)
        too_old = commit_date < datetime.datetime.strptime(self.settings['start'], '%d/%m/%Y')
        is_stale = commit_date < datetime.datetime.now() - datetime.timedelta(days=self.settings['max_days'])
        branch_name_matches = any(re.match(pattern, branch)
                                  for pattern
                                  in self.settings['name_patterns'])
        return is_stale and branch_name_matches and not too_old

    def comms_error(self):
        return False

def is_merge(branch):
    return '->' in branch


def tidy_branch(branch):
    return branch[2:] if branch.startswith('*') else branch


def latest_commit(project, branch):
    revision = project.latest_changeset(tidy_branch(branch))
    return project.repo.commit(revision)


if __name__ == '__main__':
    with open('conf.yaml') as config_file:
        settings = yaml.load(config_file)['signallers']['MERGETEST']['merge']
    m = Merge(settings)
    m.poll()
    # repo = Repo('scratch/repos/integration-services')
    # d = repo.heads['develop'].commit.committed_date
    # print(time.gmtime(d))
