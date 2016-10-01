import os
import subprocess
import errno


class GenerateDiffs():

    def from_phabricator_repos(self, path_to_repos, path_for_diffs):
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

        for repo in repos:
            filename = repo

            os.chdir(os.path.join(target_dir, repo))
            print('Working on %s' % (repo))

            try:
                p = subprocess.check_output("git diff %s %s" % (from_commit, to_commit), shell=True)
            except subprocess.CalledProcessError as e:
                if e.returncode == 128:
                    print("%s appears to be empty... skipping." % (repo, ))
                else:
                    raise e
            else:
                os.chdir("../../")
                f = open(os.path.join(dest_dir, filename + ".diff"), "wb")
                f.write(p)
                f.close()
