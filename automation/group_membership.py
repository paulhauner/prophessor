import csv
import re

class Load():
    """
    Load users, groups and their relations
    """
    def usernames(self, csv_file):
        all = self.from_csv(csv_file)
        results = []
        for e in all:
            results.append(e['User Name'])
        return results

    def users_for_group(self, csv_file, group_code):
        """
        Return a list of User Names which belong to a group
        :param csv_file: path to csv file
        :param group: Group (string)
        :return: list
        """
        groups = self.from_csv(csv_file)
        results = []
        for e in groups:
            if e['Group Code'] == group_code:
                results.append(e['User Name'])
        return results

    def unique_groups(self, csv_file):
        """
        Return a list of unique groups
        :param csv_file: path to csv file
        :return: list
        """
        groups = self.groups(csv_file)
        unique = []
        for e in groups:
            if e not in unique:
                unique.append(e)
        return unique

    def groups(self, csv_file):
        """
        Return a list of groups (will have duplicates)
        :param csv_file: path to csv file
        :return: list
        """
        all = self.from_csv(csv_file)
        return [student['Group Code'] for student in all]

    def from_csv(self, csv_file):
        """
        Returns a list of dicts with all information
        :param csv_file: path to csv file
        :return: list
        """
        file = open(csv_file)
        reader = csv.DictReader(file)
        return [row for row in reader]


class Translate():
    def get_group_number_from_group_code(self, group_code):
        code_regex = re.compile("Group_gc_(\d+)")
        result = code_regex.search(group_code)
        if result:
            return int(result.group(1))
        else:
            return None

    def get_project_name_from_group_code(self, group_code, project_part, is_marking_group):
        group_num = self.get_group_number_from_group_code(group_code)
        if group_num:
            return self.build_project_name(group_num, project_part, is_marking_group)
        else:
            return None

    def build_project_name(self, group_num, project_part, is_marking_group):
        if is_marking_group:
            return "G%02d-Part%02d-Markers" % (group_num, project_part)
        else:
            return "G%02d-Project-Part%02d" % (group_num, project_part)


load = Load()
translate = Translate()

