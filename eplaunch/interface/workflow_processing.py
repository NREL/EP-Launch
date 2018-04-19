import threading

import wx

from eplaunch.workflows.base import EPLaunch3WorkflowResponse

EVT_RESULT_ID = wx.NewId()


def event_result(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class WorkflowThread(threading.Thread):
    """Worker Thread Class."""

    def __init__(self, notify_window, workflow_instance, run_directory, file_name, main_args):
        super().__init__()
        self._notify_window = notify_window
        self._want_abort = 0
        self.workflow_instance = workflow_instance
        self.run_directory = run_directory
        self.file_name = file_name
        self.workflow_main_args = main_args
        self.start()

    def run(self):
        """Run Workflow Thread."""
        workflow_response = self.workflow_instance.main(self.run_directory, self.file_name, self.workflow_main_args)
        if type(workflow_response) is not EPLaunch3WorkflowResponse:
            workflow_response = EPLaunch3WorkflowResponse(
                success=False,
                message='Current workflow main function did not respond properly'
            )
        wx.PostEvent(self._notify_window, ResultEvent(workflow_response))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self.workflow_instance.abort = True
