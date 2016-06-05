import os

GROUP_MEMBERS_CSV = os.path.join(os.path.dirname(os.path.realpath(__file__)), "group_members.csv")

BASE_DOMAIN = "devphab.paulh.io:8081"
PHAB_API_ADDRESS = "http://" + BASE_DOMAIN

PHAB_API_TOKEN = "api-265t7eybohvvkfxidvsywwjieshr"

# super users get added to all projects
PHAB_SUPER_USER_PHIDS = ['PHID-USER-oluorlo4dyo6p7erkro7',]