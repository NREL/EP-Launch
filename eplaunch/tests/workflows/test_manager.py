import os
import tempfile
import unittest

from eplaunch.workflows.manager import get_workflows


class TestGetWorkflows(unittest.TestCase):

    def setUp(self):
        self.extra_workflow_dir = tempfile.mkdtemp()

    def test_default_behavior_with_builtins(self):
        workflows, warnings = get_workflows([], disable_builtins=False)
        self.assertTrue(len(workflows) > 0)
        self.assertEqual(0, len(warnings))

    def test_empty_workflow_response(self):
        workflows, warnings = get_workflows([], disable_builtins=True)
        self.assertEqual(len(workflows), 0)
        self.assertEqual(0, len(warnings))

    def test_valid_external_workflow(self):
        file_contents = """
from eplaunch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1
class SiteLocationWorkflow(BaseEPLaunchWorkflow1):
    def name(self): return 'dummy'
    def description(self): return 'Dummy workflow'
    def get_file_types(self): return ['*.txt']
    def get_output_suffixes(self): return []
    def get_interface_columns(self): return ['dummy']
    def main(self, run_directory, file_name, args):
        return EPLaunchWorkflowResponse1(success=True, message='Hello', column_data={'dummy': location_name})
        """
        with open(os.path.join(self.extra_workflow_dir, 'valid_workflow.py'), 'w') as f:
            f.write(file_contents)
        external_only_workflows, warnings = get_workflows([self.extra_workflow_dir], disable_builtins=True)
        self.assertEqual(len(external_only_workflows), 1)
        self.assertEqual(0, len(warnings))

    def test_invalid_workflow_bad_syntax(self):
        # note that the name function has a syntax error with a missing trailing quote on the dummy string literal
        file_contents = """
from eplaunch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1
class SiteLocationWorkflow(BaseEPLaunchWorkflow1):
    def name(self): return 'dummy
    def description(self): return 'Dummy workflow'
    def get_file_types(self): return ['*.txt']
    def get_output_suffixes(self): return []
    def get_interface_columns(self): return ['dummy']
    def main(self, run_directory, file_name, args):
        return EPLaunchWorkflowResponse1(success=True, message='Hello', column_data={'dummy': location_name})
        """
        with open(os.path.join(self.extra_workflow_dir, 'bad_syntax_workflow.py'), 'w') as f:
            f.write(file_contents)
        external_only_workflows, warnings = get_workflows([self.extra_workflow_dir], disable_builtins=True)
        self.assertEqual(len(external_only_workflows), 0)
        self.assertEqual(1, len(warnings))

    def test_invalid_workflow_bad_workflow(self):
        # note that the name function has a syntax error with a missing trailing quote on the dummy string literal
        file_contents = """
from eplaunch.workflows.base import UnknownWorkflowClass, EPLaunchWorkflowResponse1
class SiteLocationWorkflow(UnknownWorkflowClass):
    def name(self): return 'dummy'
    def description(self): return 'Dummy workflow'
    def get_file_types(self): return ['*.txt']
    def get_output_suffixes(self): return []
    def get_interface_columns(self): return ['dummy']
    def main(self, run_directory, file_name, args):
        return EPLaunchWorkflowResponse1(success=True, message='Hello', column_data={'dummy': location_name})
        """
        with open(os.path.join(self.extra_workflow_dir, 'bad_syntax_workflow.py'), 'w') as f:
            f.write(file_contents)
        external_only_workflows, warnings = get_workflows([self.extra_workflow_dir], disable_builtins=True)
        self.assertEqual(len(external_only_workflows), 0)
        self.assertEqual(1, len(warnings))
