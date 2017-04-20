import os
import subprocess
from .api import api_call


class Repository():
    def create(self, name, callsign, uri, vcs="git"):
        result = api_call.template("create_repository", (name, callsign, uri, vcs))

        # Complete creation of the repository (API does not handle this part).
        repo_dir = os.path.join("/var/repo/", callsign)
        example_repo = os.path.join(os.getcwd(), "example_files/example_repo/")
        p1 = subprocess.Popen("cp -r %s %s" % (example_repo, repo_dir,), shell=True)
        p1.wait()

        file_to_change = os.path.join(repo_dir, "hooks/pre-receive")
        p2 = subprocess.Popen("sed -i 's/CALLSIGN/%s/' %s" % (callsign, file_to_change,), shell=True)
        p2.wait()

        return result

repository = Repository()

