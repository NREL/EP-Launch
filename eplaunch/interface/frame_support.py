import os
import datetime


class FrameSupport(object):
    """
    This class provides (generally) static support methods used by the GUI.
    The intent is to extract out logic from the frame wherever possible in order to
    a) Get responsibilities in the right spot
    b) Make the logic easier to test
    """

    @staticmethod
    def get_files_in_directory(directory_name):
        file_list = []
        if directory_name:
            files = os.listdir(directory_name)
            for this_file in files:
                if this_file.startswith('.'):
                    continue
                file_path = os.path.join(directory_name, this_file)
                if os.path.isdir(file_path):
                    continue
                file_modified_time = os.path.getmtime(file_path)
                modified_time_string = datetime.datetime.fromtimestamp(file_modified_time).replace(microsecond=0)
                file_size_string = '{0:12,.0f} KB'.format(os.path.getsize(file_path) / 1024)  # size
                file_list.append({"name": this_file, "size": file_size_string, "modified": modified_time_string})
        file_list.sort(key=lambda x: x['name'])
        return file_list
