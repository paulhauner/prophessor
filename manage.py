import sys
import re
import json
from local_settings import *
from automation.group_membership import load as load_group_membership
from automation.group_membership import translate as group_translator
from automation.diffs import diffs as submitted_diffs
from phabricator.project import project as phab_project
from phabricator.user import user as phab_user
from phabricator.diff import diff as phab_diff

arg_task = sys.argv[1]


class LoadRawDiffs():
    def go(self, dir):
        diffs = submitted_diffs.get_all(dir)
        for diff in diffs:
            diff_id = self.create_diff_from_file(os.path.join(dir, diff))
            if diff_id < 0:
                print('Error creating differential with file: %s' % diff)
            else:
                self.create_revision(diff_id, diff)

    def create_revision(self, diff_id, diff_filename):
        print(submitted_diffs.get_diff_group_number(diff_filename))
        phab_diff.create_revision(diff_id, 'test_original_title')

    def create_diff_from_file(self, diff_location):
        """
        Create a phabricator diff from a file
        :param diff_location: String: Location of the file
        :return: ID of created diff if successful. -1 if failure
        """
        with open(diff_location, 'r') as file:
            data = file.read()
            return phab_diff.create_raw(diff=data)


class Enroll():
    def go(self, csv):
        """
        go creates users.
        """
        # Create users
        users = load_group_membership.from_csv(csv)
        success = self.create_users(users)
        if success:
            print('User creation completed successfully.')
        else:
            print('User creation failed.')

    def create_users(self, users):
        """
        create_users creates users in Phabricator from a Dict of users.
        :param users: Dictionary of users.
        :return: Boolean True if successful.
        """
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


class CreateProjects():
    def go(self, csv, project_part):
        self.create_projects(csv, project_part)

    def create_projects(self, csv, project_part, icon="policy", color="red"):
        """
        create_project creates projects in Phabricator from a csv.
        :param groups: A unique list of projects.
        :param icon: String of phab icon name.
        :param color: String of phab color.
        :return: None
        """
        groups = load_group_membership.unique_groups(csv)
        for group_code in groups:
            group_name = group_translator.get_project_name_from_group_code(
                group_code=group_code,
                project_part=project_part,
                is_marking_group=False
            )
            if group_name:
                usernames = load_group_membership.users_for_group(csv, group_code)
                phids = []
                for u in usernames:
                    phids.append(phab_user.get_phid_from_username(u))
                phids = phids + PHAB_SUPER_USER_PHIDS

                phab_project.create(group_name, icon, color, phids)
                print("Created group: %s" % (group_name,))
            else:
                print("Skipped: %s" % (group_code,))


# Parse arguments to do stuff

if arg_task == 'enroll':
    # python manage.py enroll group_members.csv
    action = Enroll()
    action.go(sys.argv[2])

elif arg_task == 'createprojects':
    # python manage.py createprojects group_members.csv 1234
    part = int(sys.argv[3])
    action = CreateProjects()
    action.go(sys.argv[2], part)

elif arg_task == 'loaddiffs':
    # python manage.py loaddiffs diffs/
    action = LoadRawDiffs()
    action.go(sys.argv[2])

