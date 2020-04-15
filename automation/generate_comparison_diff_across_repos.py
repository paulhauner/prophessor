import os
import subprocess
import errno


class GenerateRepoComparison():

    def from_phabricator_repos(self, path_to_repos, path_for_diffs, branch="master"):
        target_dir = path_to_repos
        dest_dir = path_for_diffs

        try:
            os.makedirs(dest_dir)
        except OSError as e:
            # raise unless we just got an exception saying the folder already exists
            if e.errno != errno.EEXIST:
                raise

        from_commit = "`git rev-list master | tail -n 1`"
        to_commit = "`git rev-list master | head -n 1`"

        repos = os.listdir(target_dir)

        empty_repos = set()
        active_repos = set()

        def is_repo_empty(repo):
            if repo in empty_repos:
                return True
            elif repo in active_repos:
                return False

            prev_cwd = os.getcwd()
            try:
                os.chdir(os.path.join(target_dir, repo))
                p = subprocess.check_output("git diff %s %s" % (from_commit, to_commit), shell=True)
            except subprocess.CalledProcessError as e:
                if e.returncode == 128:
                    print("%s appears to be empty... skipping." % (repo, ))
                    empty_repos.add(repo)
                    os.chdir(prev_cwd)
                    return True
                else:
                    raise e
            else:
                active_repos.add(repo)
                os.chdir(prev_cwd)
                return False

        for repo_i, repo in enumerate(repos):
            if is_repo_empty(repo):
                continue

            os.chdir(os.path.join(target_dir, repo))
            print('Working on %s' % repo)

            for repo_compare in repos[repo_i+1:]:
                if not is_repo_empty(repo):
                    p = subprocess.check_output("git remote add -f compare ../%s; git diff master remotes/compare/master; git remote rm compare" % (repo_compare), shell=True)
                    f = open(os.path.join(dest_dir, "%s_%s.diff" % (repo, repo_compare)), "wb")
                    f.write(p)
                    f.close()
