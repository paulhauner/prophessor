import json
from .api import api_call


class Project():
    def get_phid_from_name(self, name):
        phabed_name = "#%s" % name
        result = api_call.template("phid_lookup", "names[]=%s" % phabed_name)
        if result:
            return result[phabed_name]['phid']

    def get_users(self, project_phid):
        result = api_call.template("get_project_details", (project_phid,))
        if result:
            return json.dumps(result["data"][project_phid]["members"])

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

project = Project()

