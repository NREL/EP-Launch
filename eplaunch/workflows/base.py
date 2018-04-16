class BaseEPLaunch3Workflow(object):

    def name(self):
        raise NotImplementedError("name function needs to be implemented in derived workflow class")

    def description(self):
        raise NotImplementedError("description function needs to be implemented in derived workflow class")

    def get_file_types(self):
        raise NotImplementedError("get_file_types needs to be implemented in derived workflow class")

    def get_extra_data(self):
        """
        Allows a dictionary of extra data to be generated, defaults to empty so it is not required
        :return: Dictionary of string, string
        """
        return {}

    def get_interface_columns(self):
        """
        Returns an array of column names for the interface; defaults to empty so it is not required
        :return:
        """
        return []
