import re
import json
import time
from .database import db
from .arcanist import arc

diff_revision_policy_update_sql = """UPDATE default_differential.differential_revision
    SET viewPolicy = %s,editPolicy = %s
    WHERE id = %s"""

class Diff():
    def create_raw(self, diff):
        """
        Create a diff using arc.
        :param diff: The contents of the dif
        :return: ID of created diff if successful. -1 if failure
        """
        result = arc.call_and_pipe_in(['diff', '--raw'], diff)
        id_regex = re.compile("/differential/diff/(\d+)/")
        regex_result = id_regex.search(result)
        if regex_result:
            diff_id = int(regex_result.group(1))
            return diff_id
        else:
            print(result)
            return -1

    def create_revision(self, diff_id, **kwargs):
        """
        create_revision creates a Phab Differential Revision for the given diff_id
        :param diff_id: The diff id (not phid)
        :param kwargs: The values to be passed into the 'fields' section of the conduit call
        :return: The revision id (not phid)
        """
        json_data = json.dumps(
            {
                'diffid': diff_id,
                'fields': kwargs
            }
        )
        json_result = arc.call_and_pipe_in(['call-conduit', 'differential.createrevision'], json_data)
        result = json.loads(json_result)
        return result['response']['revisionid']

    def set_revision_policy(self, revision_id, view_policy, edit_policy):
        connection = db.connect()

        with connection.cursor() as cursor:
            cursor.execute(diff_revision_policy_update_sql, (view_policy, edit_policy, revision_id))

        db.commit(connection)
        db.disconnect(connection)

diff = Diff()
