class BaseWorkflow(object):

    def name(self):
        raise NotImplementedError("name function needs to be implemented in derived workflow class")

    def description(self):
        raise NotImplementedError("description function needs to be implemented in derived workflow class")

    def entry_point(self):
        raise NotImplementedError("entry_point needs to be implemented in derived workflow class")

    def get_file_types(self):
        raise NotImplementedError("get_file_types needs to be implemented in derived workflow class")

    def get_extra_data(self):
        """
        Allows a dictionary of extra data to be generated, defaults to empty so it is not required
        :return: Dictionary of string, string
        """
        return {}
