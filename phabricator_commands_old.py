import subprocess
import time
import string
import pymysql.cursors
import re
import random
import json
import urllib



#connection = pymysql.connect(host="phabdb", user="admin", password="lkj6alkj56a3njhauijlz", cursorclass=pymysql.cursors.DictCursor)

create_subgroup = "https://" + base_domain + "/project/edit/?name=G%02d-Project-Part1&description=Project%%20covering%%20part%%20one%%20of%%20the%%20ELEC5616%%20project.%%20This%%20phabricator%%20project%%20is%%20a%%20subproject%%20of%%20your%%20Group%02d%%20project.&icon=policy&color=red&policy.view=PHID-PLCY-om6umpwirq3di3akyt6q&policy.edit=admin&policy.join=no-one&parent=%d"

create_group = "https://" + base_domain + "/project/edit/?name=Group%02d&description=Project%%20for%%20members%%20of%%20Group%02d&icon=group&color=green&policy.view=PHID-PLCY-om6umpwirq3di3akyt6q&policy.edit=admin&policy.join=no-one"

create_marker_group = "https://" + base_domain + "/project/edit/?name=G%02d-Part2-Markers&description=Project%%20including%%20those%%20who%%20must%%20provide%%20feedback%%20on%%20part%%20two%%20of%%20Group%02d's%%20project&icon=bugs&color=yellow&policy.view=PHID-PLCY-om6umpwirq3di3akyt6q&policy.edit=admin&policy.join=no-one&members=%s"

base_number = 8



# e.type = 13 -- 13 is the membership edge type
# p.status = 0 -- 0 means the project is active (not archived)
phab_users_projects_sql = """SELECT u.userName AS user_name, ue.address AS email_address, u.phid AS user_phid, p.name AS project_name
                    FROM default_user.user u
                    JOIN default_user.user_email ue ON u.phid = ue.userPHID
                    JOIN default_project.edge e ON u.phid = e.dst
                    JOIN default_project.project p ON e.src = p.phid
                    WHERE p.status = 0 AND e.type = 13"""

phab_user_projects_sql = phab_users_projects_sql + " AND u.userName = %s"

phab_repository_view_sql = """SELECT r.id, r.phid, r.name, r.viewPolicy AS view_policy_phid, pv.name AS view_policy_project, r.editPolicy AS edit_policy_phid, pe.name AS edit_policy_project
                    FROM default_repository.repository r
                    LEFT JOIN default_project.project pv ON pv.phid = r.viewPolicy
                    LEFT JOIN default_project.project pe ON pe.phid = r.editPolicy"""

phab_find_project_by_name_prefix_sql = """SELECT p.id, p.phid, p.name FROM default_project p WHERE p.name LIKE "%s%%"""

phab_api_templates = {
    "remove_user_from_project": {
        "method": "project.edit",
        "data": "api.token=" + phab_api_token + "&transactions[0][type]=members.remove&transactions[0][value][0]=%s&objectIdentifier=%s",
        "args": ("user_phid", "group_phid")
        },
    "add_user_to_project": {
        "method": "project.edit",
        "data": "api.token=" + phab_api_token + "&transactions[0][type]=members.add&transactions[0][value][0]=%s&objectIdentifier=%s",
        "args": ("user_phid", "group_phid")
        },
    "make_project_subproject": {
        "method": "project.edit",
        "data": "api.token=" + phab_api_token + "&transactions[0][type]=parent&transactions[0][value]=%s&objectIdentifier=%s",
        "args": ("parent_phid", "child_phid")
        },
    "get_project_details": {
        "method": "project.query",
        "data": "api.token=" + phab_api_token + "&names[]=%s",
        "args": ("group_name")
    },
    "create_project": {
        "method": "project.create",
        "data": "api.token=" + phab_api_token + "&name=%s&icon=%s&color=%s%s",
        "args": ("name", "icon", "color", "members[]=%s")
    }
}

def get_database_cursor():
    return connection.cursor()

def call_api(method, data):
    return subprocess.check_output("echo '%s' | arc call-conduit --conduit-uri %s --conduit-token %s %s" % (json.dumps(data), phab_api_address, phab_conduit_token, method), shell=True)

def call_api_raw(method, data_string):
    print("API CALL:  %s -- %s" % (method, data_string))
    return subprocess.check_output(["curl", "-s", phab_api_address + "/api/" + method, "-d", data_string])

def call_api_template(template_name, args):
    response = json.loads(call_api_raw(phab_api_templates[template_name]["method"], phab_api_templates[template_name]["data"] % args).decode("ascii"))
    if response["error_code"]:
        raise Exception("Call to API Template %s resulted in an error code: %s (%s)" % (template_name, str(response["error_code"]), response["error_info"]))
    return response["result"]

def open_group_tabs(n, fr=1):
    for i in range(fr, fr+n):
        subprocess.run(["google-chrome-stable", create_group % (i,i)])

def open_subgroup_tab(group_num, base_num=base_number):
    subprocess.run(["google-chrome-stable", create_subgroup % (group_num,group_num,(base_num+2*group_num))])
    
def open_marker_group_tab(group_num, members=[]):
    subprocess.run(["google-chrome-stable", create_marker_group % (group_num,group_num,",".join(members))])


def get_user_group_membership(show_email=False):
    cursor = get_database_cursor()

    cursor.execute(phab_users_projects_sql)

    group_regex = re.compile("Group(\d+)")
    group_membership = {}

    for result in cursor.fetchall():
        found = group_regex.search(str(result["project_name"]))
        if found:
            if show_email:
                group_membership[result["email_address"]] = int(found.group(1))
            else:
            else:
                group_membership[result["user_name"]] = int(found.group(1))

    return group_membership

def get_user_project_membership(username):
    cursor = get_database_cursor()

    cursor.execute(phab_user_projects_sql, (username,))

    project_membership = []

    for result in cursor.fetchall():
        project_membership.append(result.get("project_name"))

    return project_membership

def get_random_marking_allocations(allocation_count=2):
    # Excludes people from marking their own groups
    group_membership = get_user_group_membership()
    groups = list(set(group_membership.values()))
    users = list(group_membership.keys())
    group_allocations = {group_num: [] for group_num in groups}
    users_to_allocate = list()
    for i in range(allocation_count):
        users_to_allocate.extend(users)
    random.shuffle(users_to_allocate)

    def can_mark_group(user, group_idx):
        if group_membership[user] == groups[group_idx]:
            # User is in group
            return False
        elif user in group_allocations[groups[group_idx]]:
            # User is already marking group
            return False
        else:
            return True
            


    group_index = 0
    while len(users_to_allocate):
        cur_user = users_to_allocate.pop()
        if can_mark_group(cur_user, group_index):
            group_allocations[groups[group_index]].append(cur_user)
        else:
            # Find a group they can mark
            skip_users = 1
            while not can_mark_group(cur_user, group_index):
                users_to_allocate.insert(skip_users, cur_user)
                cur_user = users_to_allocate.pop()
                skip_users += 1

            group_allocations[groups[group_index]].append(cur_user)
        group_index += 1
        group_index %= len(groups)

    return group_allocations


def open_marking_allocation_tabs():
    marking_allocation = {1: ['minnie1', 'mkaw9789', 'kshr9810', 'awong', 'Tarm'], 2: ['farfromnear', 'psha7619', 'evemj', 'Xathereal', 'aguo7027'], 3: ['qnie3938', 'kristy', 'pediy', 'kla_', 'Mutsuki'], 4: ['lemmings', 'Emily', 'fbakhtiyar', 'jyan3977', 'evemj'], 5: ['memes', 'kristy', 'mpax6328', 'Einstein', 'Xathereal'], 6: ['yhem7754', 'jyting', 'kla_', 'ewbuzby', '312076274'], 7: ['OolonColluphid', 'aguo7027', 'Winton1992', 'wym0207', 'hildaliu'], 8: ['raiken8817', 'vampire0z', 'feye0451', 'ele5616Alpaca', 'Jezzamon'], 9: ['Nathan', 'akuma', 'lch17030', 'raiken8817', 'memes'], 10: ['430191969', 'qapn', 'dzmliuyi', 'vina2679', 'mike'], 11: ['yurkah', 'yilu3867', 'Cabr', 'morr1561', 'gmcf8558'], 12: ['Einstein', 'vampire0z', 'cnat5672', 'akuma', 'tyler_h'], 13: ['mistty', 'plin7498', 'lukeflanno', 'ele5616Alpaca', 'farfromnear'], 14: ['chx456', 'keli9028', 'cnat5672', 'wym0207', 'brandon.r.g'], 15: ['kanykey', 'Tom01', 'dzmliuyi', 'yurkah'], 16: ['ja150', 'mattio', 'Mutsuki', 'jyting'], 17: ['lch17030', 'lukeflanno', 'lykeleanor', 'ediebold'], 18: ['hildaliu', 'addy987', 'bosen', 'nick'], 19: ['fbakhtiyar', 'kkoh6488', 'eddiez9', 'ejwmoreau'], 20: ['vina2679', 'morr1561', 'binzidd', 'mattio'], 21: ['prvndcruz', 'ewbuzby', 'Sp3000', 'pediy'], 22: ['tyler_h', '123456', 'iMonkey', 'yhem7754'], 23: ['ediebold', 'zzho2012', 'clia5292', 'Sp3000'], 24: ['huishoumys', 'Cabr', 'nyanthitlwin', '460110307'], 25: ['ja150', 'keli9028', 'PreetBrar', 'mpax6328'], 26: ['Winton1992', 'nick', 'nyanthitlwin', '460110307'], 27: ['eddiez9', 'qapn', 'PreetBrar', 'zzho2012'], 28: ['kkoh6488', 'Tom01', 'lykeleanor', 'addy987'], 29: ['awong', 'jyan3977', 'mike', 'gmcf8558'], 30: ['brandon.r.g', '123456', 'ejwmoreau', 'yilu3867'], 31: ['lwil4351', 'lche3028', 'jguo4890', 'chx456'], 32: ['kanykey', 'mistty', 'Nathan', 'Jezzamon'], 34: ['plin7498', 'iMonkey', 'lwil4351', 'prvndcruz'], 35: ['binzidd', 'schow', 'red_flag', 'clia5292'], 36: ['312076274', 'schow', 'Tony', 'bosen'], 37: ['Emily', 'minnie1', 'red_flag', '430191969'], 38: ['lche3028', 'kshr9810', 'mkaw9789', 'huishoumys'], 39: ['lemmings', 'OolonColluphid', 'feye0451', 'qnie3938'], 40: ['jguo4890', 'psha7619', 'Tarm', 'Tony']} 
    for group, markers in marking_allocation.items():
        open_marker_group_tab(group, markers)

def open_marking_allocation_tabs_part2():
    marking_allocation = {1: ['mattio', 'chx456', 'cnat5672', 'lemmings', 'Winton1992'], 2: ['feye0451', 'vampire0z', 'qapn', 'zzho2012', 'kkoh6488'], 3: ['Cabr', 'keli9028', 'mike', 'wym0207', 'memes'], 4: ['lukeflanno', '460395236', 'kristy', 'mkaw9789', 'jyting'], 5: ['gmcf8558', 'Tom01', 'yilu3867', 'Einstein', 'vina2679'], 6: ['Sp3000', 'lwil4351', 'Mutsuki', 'nick', 'eddiez9'], 7: ['qnie3938', 'plin7498', '312076274', 'memes'], 8: ['ejwmoreau', '460110307', 'clia5292', 'kkoh6488'], 9: ['ele5616Alpaca', 'Einstein', 'binzidd', 'Tony'], 10: ['nyanthitlwin', 'mpax6328', 'Xathereal', 'PreetBrar'], 11: ['yurkah', '430191969', 'nyanthitlwin', 'morr1561'], 12: ['lche3028', 'kanykey', 'mike', '123456'], 13: ['Emily', 'lch17030', 'tyler_h', 'iMonkey'], 14: ['yurkah', 'vina2679', 'psha7619', '460395236'], 15: ['hildaliu', 'Tarm', 'prvndcruz', 'ja150'], 16: ['wym0207', 'addy987', 'farfromnear', 'schow'], 17: ['ediebold', 'ele5616Alpaca', 'huishoumys', 'lemmings'], 18: ['Nathan', 'aguo7027', 'kshr9810', 'dzmliuyi'], 19: ['fbakhtiyar', 'yhem7754', 'lche3028', 'Tom01'], 20: ['zzho2012', 'feye0451', 'jyan3977', 'kanykey'], 21: ['qapn', 'plin7498', 'fbakhtiyar', 'awong'], 22: ['Cabr', 'kla_', 'kristy', 'brandon.r.g'], 23: ['aguo7027', 'ejwmoreau', 'ediebold', 'lykeleanor'], 24: ['binzidd', 'keli9028', 'raiken8817', 'Winton1992'], 25: ['yhem7754', 'prvndcruz', 'mattio', 'farfromnear'], 26: ['lwil4351', 'nick', '430191969', 'Xathereal'], 27: ['raiken8817', 'schow', 'mistty', 'jguo4890'], 28: ['jguo4890', 'akuma', 'tyler_h', 'eddiez9'], 29: ['PreetBrar', 'kla_', 'gmcf8558', 'morr1561'], 30: ['460110307', 'Tarm', 'Nathan', 'psha7619'], 31: ['dzmliuyi', 'kshr9810', 'lch17030', 'huishoumys'], 32: ['Sp3000', 'pediy', 'Mutsuki', 'red_flag'], 35: ['bosen', 'vampire0z', 'akuma', 'red_flag'], 36: ['jyan3977', 'jyting', 'chx456', 'mkaw9789'], 37: ['awong', 'qnie3938', 'hildaliu', 'pediy'], 38: ['312076274', 'iMonkey', 'mistty', 'yilu3867'], 39: ['123456', 'bosen', 'clia5292', 'Emily'], 40: ['ja150', 'lykeleanor', 'Tony', 'lukeflanno'], 41: ['mpax6328', 'cnat5672', 'addy987', 'brandon.r.g']}
    for group, markers in marking_allocation.items():
        open_marker_group_tab(group, markers)


def find_projects_by_group_num(group_number):
    phab_find_project_by_name_prefix_sql = """SELECT p.id, p.phid, p.name FROM default_project.project p WHERE p.name LIKE 'G%s%%'"""
    cursor = get_database_cursor()
    cursor.execute(phab_find_project_by_name_prefix_sql % (group_number,))
    projects = []
    for result in cursor.fetchall():
        projects.append((result["phid"].decode('ascii'), str(result["name"])))
    return projects


def insert_new_project_policy(project_phids=[]):
    if not project_phids:
        return

    new_phid = "PHID-PLCY-lukecustom%s" % (''.join([random.choice(string.ascii_letters + string.digits) for _ in range(10)]),)
    rules = [{
                "action": "allow",
                "rule": "PhabricatorProjectsPolicyRule",
                "value": project_phids
            }]
    timestamp = int(time.time())

    insert_sql = """INSERT INTO default_policy.policy 
                        (phid, rules, defaultAction, dateCreated, dateModified)
                    VALUES (%s, %s, "deny", %s, %s)"""

    cursor = get_database_cursor()
    cursor.execute(insert_sql, (new_phid, json.dumps(rules), timestamp, timestamp))
    return new_phid


def expand_view_policies_of_repositories_and_diffs():
    cursor = get_database_cursor()

    cursor.execute(phab_repository_view_sql)

    group_regex = re.compile("^G(\d+)-Project-Part2")
    proj_phid_regex = re.compile("^PHID-PROJ")

    policy_update_sql = """UPDATE default_repository.repository
                                SET viewPolicy = %s
                                WHERE id = %s"""

    diff_policy_update_sql = """UPDATE default_differential.differential_revision
                                SET viewPolicy = %s
                                WHERE viewPolicy = %s"""

    for result in cursor.fetchall():
        editable_by_group = group_regex.search(str(result["edit_policy_project"]))
        viewable_by_proj = proj_phid_regex.search(result["view_policy_phid"].decode('ascii'))
        if editable_by_group and viewable_by_proj:
            print("Editing %s" % (str(result["name"]),))
            group_projects = find_projects_by_group_num(editable_by_group.group(1))
            group_project_phids = [p[0] for p in group_projects]
            group_project_names = [p[1] for p in group_projects]
            print("    groups found: %s" % (", ".join(group_project_names),))
            new_policy_phid = insert_new_project_policy(group_project_phids)
            print("    new policy: %s" % (new_policy_phid,))
            cursor.execute(policy_update_sql, (new_policy_phid, result["id"]))
            print("    view policy updated!")
            print("    ... now updating diffs too.")
            cursor.execute(diff_policy_update_sql, (new_policy_phid, result["edit_policy_phid"].decode('ascii')))
        else:
            print("Skipping %s" % (str(result["name"])))
            print(editable_by_group)
            print(viewable_by_proj)
            print(result["view_policy_phid"])
        connection.commit()


def expand_view_policies_of_remaining_diffs():
    cursor = get_database_cursor()

    cursor.execute("""SELECT r.id, r.phid, r.viewPolicy, p.name AS project_name
                        FROM default_differential.differential_revision r
                        LEFT JOIN default_project.project p ON r.viewPolicy = p.phid
                        WHERE r.viewPolicy LIKE "PHID-PROJ%" """)

    group_regex = re.compile("^G(\d+)-Project-Part2")
    proj_phid_regex = re.compile("^PHID-PROJ")

    diff_policy_update_sql = """UPDATE default_differential.differential_revision
                                SET viewPolicy = %s
                                WHERE viewPolicy = %s"""

    for result in cursor.fetchall():
        project_group = group_regex.search(result["project_name"])
        print("Editing %s" % (str(result["title"]),))
        group_projects = find_projects_by_group_num(project_group.group(1))
        group_project_phids = [p[0] for p in group_projects]
        group_project_names = [p[1] for p in group_projects]
        print("    groups found: %s" % (", ".join(group_project_names),))
        new_policy_phid = insert_new_project_policy(group_project_phids)
        print("    new policy: %s" % (new_policy_phid,))
        print("    updating diff policies.")
        cursor.execute(diff_policy_update_sql, (new_policy_phid, result["viewPolicy"].decode('ascii')))
        connection.commit()
    
def get_project_phids_for_name(project_name, exact=True):
    cursor = get_database_cursor()
    if exact:
        cursor.execute("SELECT p.phid FROM default_project.project p WHERE p.name = %s", (project_name,))
        return cursor.fetchone().get("phid").decode("ascii")
    else:
        cursor.execute("SELECT p.phid FROM default_project.project p WHERE p.name LIKE %s", ("%" + project_name + "%",))
        return [row.get("phid").decode("ascii") for row in cursor.fetchall()]

def get_phid_for_username(username):
    cursor = get_database_cursor()
    cursor.execute("SELECT u.phid FROM default_user.user u WHERE u.userName = %s", (username,))
    return cursor.fetchone().get("phid").decode("ascii")


def get_project_phids_for_name(project_name, exact=True):
    cursor = get_database_cursor()
    if exact:
        cursor.execute("SELECT p.phid FROM default_project.project p WHERE p.name = %s", (project_name,))
        return cursor.fetchone().get("phid")
    else:
        cursor.execute("SELECT p.phid FROM default_project.project p WHERE p.name LIKE %s", ("%" + project_name + "%",))
        return [row.get("phid") for row in cursor.fetchall()]

def get_random_tutor_marking_allocations(tutor_usernames=[]):
    if not tutor_usernames:
        raise Exception("No tutor usernames?")
    num_of_tutors = len(tutor_usernames)
    user_group_membership = get_user_group_membership()
    groups = list(set(user_group_membership.values()))
    num_of_groups = len(groups)
    tutors = [(uname, get_phid_for_username(uname)) for uname in tutor_usernames]
    groups_to_be_allocated = list(groups)
    random.shuffle(groups_to_be_allocated)
    tutor_allocations = {tutor: [] for tutor in tutors}

    tutor_index = 0
    while len(groups_to_be_allocated):
        cur_group = groups_to_be_allocated.pop()
        tutor_allocations[tutors[tutor_index]].append(cur_group)
        tutor_index += 1
        tutor_index %= len(tutors)

    return tutor_allocations


def allocate_tutors_to_marking_groups(allocations):
    for tutor, groups in allocations.items():
        print("Allocating %s to groups: ", end="")
        for group in groups:
            print(str(group) + ", ", end="")
            proj_phid = get_project_phids_for_name("G%02d-Part2-Markers" % (group,))
            add_user_to_project(tutor[1], proj_phid)
            print("done!")


def remove_user_from_project(user_phid, project_phid):
    return call_api_template("remove_user_from_project", (user_phid, project_phid))

def add_user_to_project(user_phid, project_phid):
    return call_api_template("add_user_to_project", (user_phid, project_phid))

def remove_tutors_from_all_marking_groups(tutors=[]):
    marking_regex = re.compile("Markers$")
    for tutor in tutors:
        tutor_groups = get_user_project_membership(tutor)
        print("Tutor: %s is in %d groups..." % (tutor, len(tutor_groups)))
        for group in tutor_groups:
            print("     %s" % (group), end="")
            found = marking_regex.search(group)
            if found:
                remove_user_from_project(get_phid_for_username(tutor), get_project_phids_for_name(group))
                print(" ... removed.")
            else:
                print(" ... ignored.")

def create_project(name, icon="policy", color="red", members=[]):
    if members:
        return call_api_template("create_project", (name, icon, color, "&" + "&".join(["members[]=%s" % (m,) for m in members])))
    else:
        return call_api_template("create_project", (name, icon, color, ""))

def make_project_a_subproject(parent_phid, child_phid):
    return call_api_template("make_project_subproject", (parent_phid, child_phid))


def create_part2_groups(first_group_num=1, last_group_num=41):
    for group_num in range(first_group_num, last_group_num+1):
        group_name = "Group%02d" % (group_num,)
        print("Creating Part2 project for %s... " % (group_name,), end="")
        results = call_api_template("get_project_details", (group_name,))
        if not results["data"]:
            #Results aref none
            print("NOT FOUND! (doesn't exist?)")
            continue
        proj_id, proj_deets = results["data"].popitem()
        if group_name != proj_deets["name"]:
            raise Exception("Project names don't match! %s - %s" % (group_name, proj_deets["name"]))
        if proj_deets["color"] == "disabled":
            # Project is archived, skip it.
            print("SKIPPED! (because archived)")
            continue
        result = create_project("G%02d-Project-Part2" % (group_num,), icon="tag", color="orange", members=proj_deets["members"])
        print("done: %d: %s - %s" % (result["id"], result["name"], result["phid"]))

def create_projects_from_blackboard_csv(csv_reader, icon="policy", color="red"):
    for group in csv_reader:
        group_code = group["Group Code"]
        code_regex = re.compile("Project_gc_Group_gc_(\d+)")
        result = code_regex.search(group_code)
        if result:
            group_num = int(result.group(1))
            group_name = "G%02d-Project-Part1" % (group_num,)
            create_project(group_name, icon, color)
            print("Created group: %s" % (group_name,))
        else:
            print("Skipped: %s" % (group_code,))



