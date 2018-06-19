import os


class FileNameManipulation(object):

    def remove_leading_period(self, extension):
        if len(extension) > 0 and extension[0] == ".":
            extension = extension[1:]
        return extension

    def replace_extension_with_suffix(self, file_path, substitute_suffix):
        root, _ = os.path.splitext(file_path)
        return root + substitute_suffix
