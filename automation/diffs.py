import os
import re
from .group_membership import translate


class Diffs():
    def get_all(self, dir):
        files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]  # get all files in dir
        return [f for f in files if f.endswith('.diff')]  # get files with .diff extension

    def get_diff_group_number(self, filename, callsign_mappings=[]):
	# try and see if it's a callsign first
	for mapping in callsign_mappings:
            if mapping['callsign'] + '.diff' in filename:
		return translate.get_group_number_from_project_name(mapping['name'])
	# if its not a callsign. try and resolve it otherwise
	code_regex = re.compile("Group (\d+)_")
        result = code_regex.search(filename)
        if result:
            return int(result.group(1))
        else:
            return None

diffs = Diffs()
