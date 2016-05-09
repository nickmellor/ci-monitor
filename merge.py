from logger import logger
import re
import os
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
        # self.refresh_projects()
        unmerged_branches = []
        for deploy_branch_name in ['develop']:
            for project in self.projects:
                logger.info("Scanning repo for project '{0}'".format(project.repo._working_tree_dir.split(os.path.sep)[-1]))
                # project.repo.remotes.origin.fetch() -- has timeout at present
                deploy_rev = latest_commit(project, deploy_branch_name).hexsha
                for branch in self.branches(project):
                    # logger.info('Processing branch {0}'.format(branch))
                    release_rev = latest_commit(project, branch).hexsha
                    if not project.repo.is_ancestor(release_rev, deploy_rev):
                        unmerged_branches.append((project.repo._working_tree_dir.split(os.path.sep)[-1], branch))
        print(unmerged_branches)

    def merged(self, project, branch, master):
        branch_changeset = project.latest_changeset(branch)
        shared_changeset = project.shared_changeset(branch, master)
        return branch_changeset == shared_changeset[0].hexsha

    def branches(self, project):
        branches_and_merges = (tidy_branch(branch) for branch in project.remote_branches(project.repo))
        yield from (branch for branch in project.remote_branches(project.repo)
                    if not is_merge(branch) and self.fits_criteria(project, branch))

    def refresh_projects(self):
        self.clear_repos()
        for repo_uri in self.settings['repos']:
            self.gitclone(repo_uri, self.repo_dir())

    def clear_repos(self):
        os.removedirs(self.repo_dir())

    def repo_dir(self):
        return os.path.normpath(self.settings['location'])

    def gitclone(self, uri, directory):
        Repo.clone_from(uri, directory)

    def fits_criteria(self, project, branch):
        commit = latest_commit(project, branch)
        commit_date = datetime.datetime.fromtimestamp(commit.committed_date)
        too_old = commit_date < datetime.datetime.strptime(self.settings['start'], '%d/%m/%Y')
        is_stale = commit_date < datetime.datetime.now() - datetime.timedelta(days=self.settings['max_days'])
        branch_name_matches = any(re.match(pattern, branch)
                                  for pattern
                                  in self.settings['name_patterns'])
        return is_stale and branch_name_matches and not too_old


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
