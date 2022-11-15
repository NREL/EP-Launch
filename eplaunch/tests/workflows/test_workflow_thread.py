from os.path import join
from tempfile import mkdtemp
from unittest import TestCase

from eplaunch.workflows.workflow_thread import WorkflowThread
from eplaunch.workflows.base import EPLaunchWorkflowResponse1


class MockWorkflow:

    def __init__(self, mock_return_value):
        self.return_value = mock_return_value

    def main(self, _, __, ___):
        if self.return_value is None:
            raise ValueError('bad return value')
        return self.return_value

    def abort(self):
        pass


class TestWorkflowThread(TestCase):
    def setUp(self) -> None:
        self.thread_response = None

    def mock_callback(self, thread_response):
        self.thread_response = thread_response

    def test_workflow_thread_interface(self):
        temp_dir = mkdtemp()
        temp_file = join(temp_dir, 'hello')
        # call a properly operating workflow
        workflow_returns_properly = MockWorkflow(EPLaunchWorkflowResponse1(True, '', []))
        w = WorkflowThread(
            identifier=123, workflow_instance=workflow_returns_properly, run_directory=temp_dir, file_name=temp_file,
            main_args={'workflow location': '/foo/bar'}, done_callback=self.mock_callback
        )
        w.run()
        self.assertIsInstance(self.thread_response, EPLaunchWorkflowResponse1)
        # now try one that returns a bad value
        self.thread_response = None
        workflow_returns_weird_value = MockWorkflow(3.14)
        w = WorkflowThread(
            identifier=123, workflow_instance=workflow_returns_weird_value, run_directory=temp_dir, file_name=temp_file,
            main_args={'workflow location': '/foo/bar'}, done_callback=self.mock_callback
        )
        w.run()
        self.assertIsInstance(self.thread_response, EPLaunchWorkflowResponse1)
        # now try one that throws
        self.thread_response = None
        workflow_throws = MockWorkflow(None)
        w = WorkflowThread(
            identifier=123, workflow_instance=workflow_throws, run_directory=temp_dir, file_name=temp_file,
            main_args={'workflow location': '/foo/bar'}, done_callback=self.mock_callback
        )
        w.run()
        self.assertIsInstance(self.thread_response, EPLaunchWorkflowResponse1)
        # the base workflow has an abort method, just exercise this interface on the thread layer
        w.abort()
