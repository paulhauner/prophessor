import subprocess
import json
from local_settings import PHAB_API_ADDRESS, PHAB_API_TOKEN

phab_api_templates = {
    "remove_user_from_project": {
        "method": "project.edit",
        "data": "api.token=" + PHAB_API_TOKEN + "&transactions[0][type]=members.remove&transactions[0][value][0]=%s&objectIdentifier=%s",
        "args": ("user_phid", "group_phid")
        },
    "add_user_to_project": {
        "method": "project.edit",
        "data": "api.token=" + PHAB_API_TOKEN + "&transactions[0][type]=members.add&transactions[0][value][0]=%s&objectIdentifier=%s",
        "args": ("user_phid", "group_phid")
        },
    "make_project_subproject": {
        "method": "project.edit",
        "data": "api.token=" + PHAB_API_TOKEN + "&transactions[0][type]=parent&transactions[0][value]=%s&objectIdentifier=%s",
        "args": ("parent_phid", "child_phid")
        },
    "get_project_details": {
        "method": "project.query",
        "data": "api.token=" + PHAB_API_TOKEN + "&names[]=%s",
        "args": ("group_name")
    },
    "create_project": {
        "method": "project.create",
        "data": "api.token=" + PHAB_API_TOKEN + "&name=%s&icon=%s&color=%s%s",
        "args": ("name", "icon", "color", "members[]=%s")
    },
    "phid_lookup": {
        "method": "phid.lookup",
        "data": "api.token=" + PHAB_API_TOKEN + "&%s",
        "args": ("name[]=%s",)
    },
    "create_repository": {
        "method": "repository.create",
        "data": "api.token=" + PHAB_API_TOKEN + "&name=%s&vcs=%s",
        "args": ("name", "icon")
    },
}


class Call():
    def raw(self, method, data_string):
        print("API CALL:  %s -- %s" % (method, data_string))
        return subprocess.check_output(["curl", "-s", PHAB_API_ADDRESS + "/api/" + method, "-d", data_string])

    def template(self, template_name, args):
        response = json.loads(self.raw(phab_api_templates[template_name]["method"],
                                           phab_api_templates[template_name]["data"] % args).decode("ascii"))
        if response["error_code"]:
            raise Exception("Call to API Template %s resulted in an error code: %s (%s)" % (
            template_name, str(response["error_code"]), response["error_info"]))
        return response["result"]

api_call = Call()