import os
from .api import api_call
from subprocess import Popen

CREATE_STUDENT_PHP_SCRIPT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "create_student.php")

class User:
    def get_phid_from_username(self, username):
        phabed_username = "@%s" % username
        result = api_call.template("phid_lookup", "names[]=%s" % phabed_username)
        return result[phabed_username]['phid']

    def create(self, username, password, fullname, email):
        process = Popen([CREATE_STUDENT_PHP_SCRIPT, username, password, fullname, email])
        process.wait()
        return process.returncode

user = User()