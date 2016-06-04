import os

GROUP_MEMBERS_CSV = os.path.join(os.path.dirname(os.path.realpath(__file__)), "group_members.csv")

BASE_DOMAIN = "devphab.paulh.io:8081"
PHAB_API_ADDRESS = "http://" + BASE_DOMAIN

PHAB_API_TOKEN = "api-d7blns4fwk27len2wxndbry4c5t2"

# super users get added to all projects
PHAB_SUPER_USER_PHIDS = ['PHID-USER-coo6jmgywc5e2ffmagou',]