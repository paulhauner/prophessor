import os
from subprocess import Popen

CREATE_STUDENT_PHP_SCRIPT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "create_student.php")

class User:
    def create(self, username, password, fullname, email):
        process = Popen([CREATE_STUDENT_PHP_SCRIPT, username, password, fullname, email])
        process.wait()
        return process.returncode

user = User()