import os
import subprocess
import shutil

target_dir = "repo"
dest_dir = "diffs"
temp_dir = "temp"

from_commit = "`git rev-list HEAD | tail -n 1`"
to_commit = "`git rev-list HEAD | head -n 1`"

git_command = ["git", "config", "--local", "--bool", "core.bare"]

os.mkdir(temp_dir)
os.symlink("../" + target_dir, temp_dir + "/.git")

os.chdir(temp_dir)

subprocess.check_output(git_command + ["false"])

p = subprocess.check_output("git diff %s %s" % (from_commit, to_commit), shell=True)

subprocess.check_output(git_command + ["true"])

os.chdir("../")

shutil.rmtree(temp_dir)
