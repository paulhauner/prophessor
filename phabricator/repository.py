from .api import api_call


class Repository():
    def create(self, name, icon="policy", color="red", members=[]):
        if members:
            return api_call.template("create_project",
                                     (name, icon, color, "&" + "&".join(["members[]=%s" % (m,) for m in members])))
        else:
            return api_call.template("create_project", (name, icon, color, ""))

repository = Repository()

