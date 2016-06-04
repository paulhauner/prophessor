import csv

class Load():
    """
    Load users, groups and their relations
    """
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

load = Load()

