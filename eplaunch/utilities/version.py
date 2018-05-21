class Version:

    def check_energyplus_version(self, file_path):
        found = False
        current_version = ''
        with open(file_path, "r") as f:
            cur_line = f.readline()
            while cur_line:
                cur_line.strip()
                if cur_line[0] != "!":
                    cur_line.upper()
                    if "VERSION" in cur_line:
                        next_line = f.readline()
                        poss_obj = cur_line + next_line
                        parts = poss_obj.split(',')
                        current_version = parts[1]
                        found = True
                        break
        print("The current version is {}".format(current_version))
        return found, current_version
