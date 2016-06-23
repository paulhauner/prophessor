from database import db
import random
import string
import time
import json

insert_sql = """INSERT INTO default_policy.policy
    (phid, rules, defaultAction, dateCreated, dateModified)
VALUES (%s, %s, "deny", %s, %s)"""


class Policy():
    def create_project_policy(self, project_phids):
        return self.create([{
            'action': "allow",
            'rule': "PhabricatorProjectsPolicyRule",
            'value': project_phids
        }])

    def create(self, rules):
        connection = db.connect()
        new_phid = "PHID-PLCY-prophessor%s" % (
            ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(10)])
        )
        timestamp = int(time.time())

        with connection.cursor() as cursor:
            cursor.execute(insert_sql, (new_phid, json.dumps(rules), timestamp, timestamp))

        db.disconnect(connection)
        return new_phid

policy = Policy()
