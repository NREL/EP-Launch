import os
import glob

from eplaunch.utilities.crossplatform import Platform


class LocateWorkflows:

    def find(self):
        search_roots = {
            Platform.WINDOWS: [
                'c:\\',
                'd:\\',
                'e:\\',
                'f:\\',
                'g:\\',
                'h:\\',
                'i:\\',
                'j:\\',
                'k:\\',
                'l:\\',
                'm:\\',
                'n:\\',
                'p:\\',
                'p:\\',
                'q:\\',
                'r:\\',
                's:\\',
                't:\\',
                'u:\\',
                'v:\\',
                'w:\\',
                'x:\\',
                'y:\\',
                'z:\\',
            ],
            Platform.LINUX: [
                '/usr/local/bin/',
            ],
            Platform.MAC: [
                '/Applications/',
            ],
            Platform.UNKNOWN: [
            ]
        }
        search_names = ["EnergyPlus*", "energyplus*", "EP*", "ep*", "E+*", "e+*"]
        found_directories = set()
        for search_root in search_roots[Platform.get_current_platform()]:
            for search_name in search_names:
                full_search_path = os.path.join(search_root, search_name)
                full_search_path_with_workflow = os.path.join(full_search_path, "workflows")
                possible_directories = glob.glob(full_search_path_with_workflow)
                found_directories.update(possible_directories)
        return list(found_directories)
