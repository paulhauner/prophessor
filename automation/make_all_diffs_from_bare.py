import os
import subprocess
import shutil

target_dir = "repo"
dest_dir = "diffs"

os.makedirs(dest_dir, exist_ok=True)

from_commit = "`git rev-list master | tail -n 1`"
to_commit = "`git rev-list master | head -n 1`"

repos = os.listdir(target_dir)

for repo in repos:
    filename = repo

    os.chdir(os.path.join(target_dir, repo))
    print(repo)

    try:
        p = subprocess.check_output("git diff %s %s" % (from_commit, to_commit), shell=True)
    except subprocess.CalledProcessError as e:
        if e.returncode == 128:
            print("%s appears to be empty... skipping." % (repo, ))
        else:
            raise e
    os.chdir("../../")
    f = open(os.path.join(dest_dir, filename + ".diff"), "wb")
    f.write(p)
    f.close()
