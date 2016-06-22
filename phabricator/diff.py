import re
import json
from .arcanist import arc

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
            return -1

    def create_revision(self, diff_id, **kwargs):
        json_data = json.dumps(
            {
                'diffid': diff_id,
                'fields': kwargs
            }
        )
        json_result = arc.call_and_pipe_in(['call-conduit', 'differential.createrevision'], json_data)
        result = json.loads(json_result)
        return result['response']['revisionid']

diff = Diff()
