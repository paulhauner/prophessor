import os
import re

class Diffs():
    def get_all(self, dir):
        files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]  # get all files in dir
        return [f for f in files if f.endswith('.diff')]  # get files with .diff extension

    def get_diff_group_number(self, filename):
        code_regex = re.compile("Group (\d+)_")
        result = code_regex.search(filename)
        if result:
            return int(result.group(1))
        else:
            return None

diffs = Diffs()