import subprocess


class EPLaunchWorkflowResponse1(object):

    def __init__(self, success, message, column_data, **extra_data):
        self.id = None  # assigned by workflow thread manager
        self.success = success
        self.message = message
        self.column_data = column_data
        self.extra_data = extra_data


class BaseEPLaunchWorkflow1(object):

    def __init__(self):
        self._callback = None
        self.my_id = None
        self._process = None

    def name(self):
        raise NotImplementedError("name function needs to be implemented in derived workflow class")

    def context(self):
        raise NotImplementedError("context function needs to be implemented in derived workflow class")

    def description(self):
        raise NotImplementedError("description function needs to be implemented in derived workflow class")

    def uses_weather(self):
        """
        If it returns True, this workflow accepts a "weather" key in the arguments to the workflow
        :return: Boolean
        """
        return False

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

    def register_standard_output_callback(self, workflow_id, callback):
        """
        Used to register the callback function from the UI for standard output from this workflow.
        This function is not to be inherited by derived workflows unless they are doing something really odd.
        Workflows should simply use self.callback(message) to send messages as necessary to the GUI during a workflow.

        :param workflow_id: A unique ID assigned by the program in order to track workflows
        :param callback: The GUI function to be called with message updates
        :return: None
        """
        self.my_id = workflow_id
        self._callback = callback

    def callback(self, message):
        """
        This is the actual callback function that workflows can call when they have an update.
        Internally here there are some other parameters passed up, but that is just to further isolate the users
        from having to pass extra data during their own calls

        :param message: A message to be sent to the GUI from the workflow
        :return: None
        """
        self._callback(self.my_id, message)

    def main(self, run_directory, file_name, args) -> EPLaunchWorkflowResponse1:
        """
        The actual running operation for the workflow, should check self.abort periodically to allow exiting
        :return: Must return an EPLaunchWorkflowResponse1 instance
        """
        raise NotImplementedError("main function needs to be implemented in derived workflow class")

    def abort(self):
        if self._process:  # pragma: no cover  # not getting caught by coverage tools, not sure why
            self._process.kill()

    def execute_for_callback(self, cmd, cwd):  # pragma: no cover  # not getting caught by coverage tools, not sure why
        self._process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(self._process.stdout.readline, ""):
            yield stdout_line.strip()
        self._process.stdout.close()
        return_code = self._process.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)
