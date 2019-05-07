import json
from .api import api_call
from .database import db

project_policy_update_sql = """UPDATE default_project.project
    SET viewPolicy = %s,editPolicy = %s, joinPolicy = %s
    WHERE phid = %s"""

class Project():
    def get_phid_from_name(self, name):
        phabed_name = "#%s" % name
        result = api_call.template("phid_lookup", "names[]=%s" % phabed_name)
        if not result is None:
            return result[phabed_name]['phid']

    def get_users(self, project_phid):
        result = api_call.template("get_project_details", (project_phid,))
        if not result is None:
            return result["data"][project_phid]["members"]

    def add_user(self, user_phid, project_phid):
        return api_call.template("add_user_to_project", (user_phid, project_phid))

    def remove_user(self, user_phid, project_phid):
        return api_call.template("remove_user_from_project", (user_phid, project_phid))

    def create(self, name, icon="policy", color="red", members=[]):
        if members:
            return api_call.template("create_project",
                                     (name, icon, color, "&" + "&".join(["members[]=%s" % (m,) for m in members])))
        else:
            return api_call.template("create_project", (name, icon, color, ""))

    def set_policy(self, project_phid, view_policy, edit_policy, join_policy):
        connection = db.connect()

        with connection.cursor() as cursor:
            cursor.execute(project_policy_update_sql, (
                view_policy,
                edit_policy,
                join_policy,
                project_phid,
            ))

        db.commit(connection)
        db.disconnect(connection)


project = Project()

