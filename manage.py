import sys
import re
from local_settings import *
from automation.group_membership import load as load_group_membership
from phabricator.project import project as phab_project
from phabricator.user import user as phab_user

arg_task = sys.argv[1]


class Enroll():
    def __init__(self):
        # Create users
        users = load_group_membership.from_csv(GROUP_MEMBERS_CSV)
        success = self.create_users(users)
        if success:
            print('User creation completed successfully.')
        else:
            print('User creation failed. Exiting.')
            #return
        # Create groups and assign users
        groups = load_group_membership.unique_groups(GROUP_MEMBERS_CSV)
        self.create_projects(groups)

    def create_users(self, users):
        success = True
        for user in users:
            error = phab_user.create(
                user['User Name'],
                user['Password'],
                "%s %s" % (user['First Name'], user['Last Name']),
                user['Email']
            )
            if error:
                success = False
                print("Creating user %s %s %s failed. Attention is required." % (
                    user['User Name'],
                    user['First Name'],
                    user['Last Name']
                ))
        return success

    def create_projects(self, groups, icon="policy", color="red"):
        for group_code in groups:
            code_regex = re.compile("Project_gc_Group_gc_(\d+)")
            result = code_regex.search(group_code)
            if result:
                group_num = int(result.group(1))
                group_name = "G%02d-Project-Part1" % (group_num,)

                usernames = load_group_membership.users_for_group(GROUP_MEMBERS_CSV, group_code)
                phids = []
                for u in usernames:
                    phids.append(phab_user.get_phid_from_username(u))
                phids = phids + PHAB_SUPER_USER_PHIDS

                phab_project.create(group_name, icon, color, phids)
                print("Created group: %s" % (group_name,))
            else:
                print("Skipped: %s" % (group_code,))

if arg_task == 'enroll':
    enroll = Enroll()

