import json
import os
import requests


class Version:

    def check_energyplus_version(self, file_path):
        _, extension = os.path.splitext(file_path)
        extension = extension.upper()
        if extension == '.IDF':
            found, string_version, number_version = self.check_idf_imf_energyplus_version(file_path)
        elif extension == '.IMF':
            found, string_version, number_version = self.check_idf_imf_energyplus_version(file_path)
        elif extension == '.EPJSON':
            found, string_version, number_version = self.check_json_energyplus_version(file_path)
        else:
            found = False
            string_version = ''
            number_version = 0
        return found, string_version, number_version

    def check_idf_imf_energyplus_version(self, file_path):
        found = False
        current_version = ''
        try:
            with open(file_path, "r") as f:
                cur_line = f.readline()
                while cur_line:
                    cur_line = cur_line.strip()
                    if cur_line:
                        if cur_line[0] != "!":
                            cur_line = cur_line.upper()
                            if "VERSION" in cur_line:
                                cur_line = self.line_with_no_comment(cur_line)
                                if ";" in cur_line:
                                    poss_obj = cur_line
                                else:
                                    next_line = f.readline()
                                    next_line = next_line.strip()
                                    next_line = self.line_with_no_comment(next_line)
                                    poss_obj = cur_line + next_line
                                if poss_obj[-1] == ";":
                                    poss_obj = poss_obj[:-1]
                                fields = poss_obj.split(',')
                                current_version = fields[1]
                                found = True
                                break
                    cur_line = f.readline()  # get the next line
            return found, current_version, self.numeric_version_from_string(current_version)
        except Exception:
            return False, '', ''

    def line_with_no_comment(self, in_string):
        exclamation_point_pos = in_string.find("!")
        if exclamation_point_pos >= 0:
            out_string = in_string[0:exclamation_point_pos]
            out_string = out_string.strip()
        else:  # no explanation point found
            out_string = in_string.strip()
        return out_string

    def numeric_version_from_string(self, string_version):
        # if the version string has sha1 hash at the end remove it
        words = string_version.split("-")
        # the rest of the version number should just be separated by periods
        parts = words[0].split(".")
        numeric_version = 0
        parts = parts[:3]
        # overwrite the patch number with a zero, or append a zero patch number
        if len(parts) == 3:
            parts[2] = 0
        if len(parts) == 2:
            parts.append("0")
        for part in parts:
            numeric_version = numeric_version * 100 + int(part)
        return numeric_version

    def numeric_version_from_dash_string(self, string_version):
        # remove leading 'V' if included
        if string_version[0] == 'V':
            string_version = string_version[1:]
        # the rest of the version number should just be separated by periods
        parts = string_version.split("-")
        numeric_version = 0
        # overwrite the patch number with a zero, or append a zero patch number
        if len(parts) == 3:
            parts[2] = 0
        if len(parts) == 2:
            parts.append("0")
        for part in parts:
            numeric_version = numeric_version * 100 + int(part)
        return numeric_version

    def string_version_from_number(self, version_number):
        # converts a coded number like 50200 (fictional version 5.2) to string with leading zeros 'V050200'
        return 'V' + str(version_number).zfill(6)

    def check_json_energyplus_version(self, file_path):
        with open(file_path, "r") as readfile:
            data = json.load(readfile)
        if 'Version' in data:
            version_dict = data['Version']
            field_dict = version_dict['Version 1']
            if field_dict:
                current_version = field_dict['version_identifier']
                if current_version:
                    return True, current_version, self.numeric_version_from_string(current_version)
        return False, '', 0

    def get_github_energyplus_list_of_releases(self):
        repo_url = r'https://api.github.com/repos/NREL/energyplus/releases'
        response = requests.get(repo_url, timeout=0.5)
        data = response.json()
        # print(json.dumps(data, indent=4))
        releases = []
        for release in data:
            if not release["prerelease"]:
                print(release["tag_name"])
                releases.append(release["tag_name"])
        return releases

    def latest_release(self, releases):
        highest_numeric = -1
        highest_string = ''
        for release in releases:
            if release[0] == 'v':
                release = release[1:]
                numeric = self.numeric_version_from_string(releases)
                if numeric > highest_numeric:
                    highest_string = release
                    highest_numeric = numeric
        return highest_string, highest_numeric

