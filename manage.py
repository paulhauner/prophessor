import sys
import re
from pprint import pprint
from local_settings import *
from automation.group_membership import load as load_group_membership
from phabricator.project import project

arg_task = sys.argv[1]


class Enroll():
    def __init__(self):
        groups = load_group_membership.unique_groups(GROUP_MEMBERS_CSV)
        self.create_projects(groups)

    def create_projects(self, groups, icon="policy", color="red"):
        for group_code in groups:
            code_regex = re.compile("Project_gc_Group_gc_(\d+)")
            result = code_regex.search(group_code)
            if result:
                group_num = int(result.group(1))
                group_name = "G%02d-Project-Part1" % (group_num,)
                project.create(group_name, icon, color)
                print("Created group: %s" % (group_name,))
            else:
                print("Skipped: %s" % (group_code,))

if arg_task == 'enroll':
    enroll = Enroll()

