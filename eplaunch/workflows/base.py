class EPLaunch3WorkflowResponse(object):

    def __init__(self, success, message, column_data, **extra_data):
        self.id = None  # assigned by workflow thread manager
        self.success = success
        self.message = message
        self.column_data = column_data
        self.extra_data = extra_data


class BaseEPLaunch3Workflow(object):

    abort = False
    output_toolbar_order = None

    def __init__(self):
        self.callback = None

    def name(self):
        raise NotImplementedError("name function needs to be implemented in derived workflow class")

    def description(self):
        raise NotImplementedError("description function needs to be implemented in derived workflow class")

    def get_file_types(self):
        raise NotImplementedError("get_file_types needs to be implemented in derived workflow class")

    def get_output_suffixes(self):
        raise NotImplementedError("get_output_suffixes needs to be implemented in derived workflow class")

    def get_extra_data(self):
        """
        Allows a dictionary of extra data to be generated, defaults to empty so it is not required
        :return: Dictionary of string, string
        """
        return {}

    def get_interface_columns(self):
        """
        Returns an array of column names for the interface; defaults to empty so it is not required
        :return: A list of interface column names
        """
        return []

    def register_standard_output_callback(self, callback):
        """
        Used to register the callback function from the UI for standard output from this workflow.
        This function is not to be inherited by derived workflows unless they are doing something really odd.
        Workflows should simply use self.callback(message) to send messages as necessary to the GUI during a workflow.

        :param callback: A function to be called with a message.  Formulation: callback = f(str: s)
        :return: None
        """
        self.callback = callback

    def main(self, run_directory, file_name, args):
        """
        The actual running operation for the workflow, should check self.abort periodically to allow exiting
        :return: Should return an EPLaunch3WorkflowResponse instance
        """
        raise NotImplementedError("main function needs to be implemented in derived workflow class")
