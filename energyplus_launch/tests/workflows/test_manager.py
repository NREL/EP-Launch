import os
from pathlib import Path
import tempfile
import unittest

from energyplus_launch.workflows.manager import WorkflowManager


class TestGetWorkflows(unittest.TestCase):

    def setUp(self):
        self.extra_workflow_dir = Path(tempfile.mkdtemp())
        self.workflow_manager = WorkflowManager()

    def test_default_behavior_with_builtins(self):
        self.workflow_manager.instantiate_all_workflows(disable_builtins=False)
        self.assertTrue(len(self.workflow_manager.workflows) > 0)
        self.assertEqual(0, len(self.workflow_manager.warnings))

    def test_empty_workflow_response(self):
        self.workflow_manager.instantiate_all_workflows(disable_builtins=True)
        self.assertTrue(len(self.workflow_manager.workflows) == 0)
        self.assertEqual(0, len(self.workflow_manager.warnings))

    def test_valid_external_workflow(self):
        file_contents = """
from energyplus_launch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1
class SiteLocationWorkflow(BaseEPLaunchWorkflow1):
    def name(self): return 'dummy'
    def context(self): return 'theseWorkflows'
    def description(self): return 'Dummy workflow'
    def get_file_types(self): return ['*.txt', '*.pdf']
    def get_output_suffixes(self): return []
    def get_interface_columns(self): return ['dummy']
    def main(self, run_directory, file_name, args):
        return EPLaunchWorkflowResponse1(success=True, message='Hello', column_data={'dummy': location_name})
        """
        with open(os.path.join(self.extra_workflow_dir, 'valid_workflow.py'), 'w') as f:
            f.write(file_contents)
        self.workflow_manager.instantiate_all_workflows(
            extra_workflow_dir=self.extra_workflow_dir, disable_builtins=True
        )
        self.assertTrue(len(self.workflow_manager.workflows) > 0)
        self.assertEqual(0, len(self.workflow_manager.warnings))

    def test_invalid_workflow_bad_syntax(self):
        # note that the name function has a syntax error with a missing trailing quote on the dummy string literal
        file_contents = """
from energyplus_launch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1
class SiteLocationWorkflow(BaseEPLaunchWorkflow1):
    def name(self): return 'dummy
    def context(self): return 'theseWorkflows'
    def description(self): return 'Dummy workflow'
    def get_file_types(self): return ['*.txt']
    def get_output_suffixes(self): return []
    def get_interface_columns(self): return ['dummy']
    def main(self, run_directory, file_name, args):
        return EPLaunchWorkflowResponse1(success=True, message='Hello', column_data={'dummy': location_name})
        """
        with open(os.path.join(self.extra_workflow_dir, 'bad_syntax_workflow.py'), 'w') as f:
            f.write(file_contents)
        self.workflow_manager.instantiate_all_workflows(
            extra_workflow_dir=self.extra_workflow_dir, disable_builtins=True
        )
        self.assertTrue(len(self.workflow_manager.workflows) == 0)
        self.assertGreater(len(self.workflow_manager.warnings), 0)

    def test_invalid_workflow_bad_workflow(self):
        # note that the workflow imports a bad workflow base class
        file_contents = """
from energyplus_launch.workflows.base import UnknownWorkflowClass, EPLaunchWorkflowResponse1
class SiteLocationWorkflow(UnknownWorkflowClass):
    def name(self): return 'dummy'
    def context(self): return 'theseWorkflows'
    def description(self): return 'Dummy workflow'
    def get_file_types(self): return ['*.txt']
    def get_output_suffixes(self): return []
    def get_interface_columns(self): return ['dummy']
    def main(self, run_directory, file_name, args):
        return EPLaunchWorkflowResponse1(success=True, message='Hello', column_data={'dummy': location_name})
        """
        with open(os.path.join(self.extra_workflow_dir, 'bad_base_workflow.py'), 'w') as f:
            f.write(file_contents)
        self.workflow_manager.instantiate_all_workflows(
            extra_workflow_dir=self.extra_workflow_dir, disable_builtins=True
        )
        self.assertTrue(len(self.workflow_manager.workflows) == 0)
        self.assertGreater(len(self.workflow_manager.warnings), 0)

    def test_incomplete_workflow(self):
        # note that the workflow does not implement all the abstract methods
        file_contents = """
from energyplus_launch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1
class SiteLocationWorkflow(BaseEPLaunchWorkflow1):
    ...
        """
        with open(os.path.join(self.extra_workflow_dir, 'incomplete_workflow.py'), 'w') as f:
            f.write(file_contents)
        self.workflow_manager.instantiate_all_workflows(
            extra_workflow_dir=self.extra_workflow_dir, disable_builtins=True
        )
        self.assertTrue(len(self.workflow_manager.workflows) == 0)
        self.assertGreater(len(self.workflow_manager.warnings), 0)

    def test_energyplus_workflow(self):
        file_contents = """
from energyplus_launch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1
class SiteLocationWorkflow(BaseEPLaunchWorkflow1):
    def name(self): return 'dummy'
    def context(self): return 'theseWorkflows'
    def description(self): return 'Dummy workflow'
    def get_file_types(self): return ['*.txt']
    def get_output_suffixes(self): return []
    def get_interface_columns(self): return ['dummy']
    def main(self, run_directory, file_name, args):
        return EPLaunchWorkflowResponse1(success=True, message='Hello', column_data={'dummy': location_name})
        """
        ep_workflow_dir = self.extra_workflow_dir / 'EnergyPlus.3.1.4' / 'workflows'
        os.makedirs(ep_workflow_dir)
        with open(os.path.join(ep_workflow_dir, 'bad_base_workflow.py'), 'w') as f:
            f.write(file_contents)
        self.workflow_manager.instantiate_all_workflows(
            extra_workflow_dir=ep_workflow_dir, disable_builtins=True
        )
        self.assertTrue(len(self.workflow_manager.workflows) > 0)
        self.assertEqual(0, len(self.workflow_manager.warnings))
        self.assertEqual(1, len(self.workflow_manager.workflow_instances('theseWorkflows')))

    def test_exception_calling_workflow(self):
        file_contents = """
from energyplus_launch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1
class SiteLocationWorkflow(BaseEPLaunchWorkflow1):
    def name(self): return 'dummy'
    def context(self): raise Exception("WHAT HAPPENED!?")
    def description(self): return 'Dummy workflow'
    def get_file_types(self): return ['*.txt']
    def get_output_suffixes(self): return []
    def get_interface_columns(self): return ['dummy']
    def main(self, run_directory, file_name, args):
        return EPLaunchWorkflowResponse1(success=True, message='Hello', column_data={'dummy': location_name})
        """
        with open(os.path.join(self.extra_workflow_dir, 'exception_workflow.py'), 'w') as f:
            f.write(file_contents)
        self.workflow_manager.instantiate_all_workflows(
            extra_workflow_dir=self.extra_workflow_dir, disable_builtins=True
        )
        self.assertTrue(len(self.workflow_manager.workflows) == 0)
        self.assertIn('Unexpected error', self.workflow_manager.warnings[0])

    def test_reset_works_with_invalid_context(self):
        self.workflow_manager.instantiate_all_workflows(disable_builtins=False)
        self.assertTrue(len(self.workflow_manager.workflows) > 0)
        self.workflow_manager.reset_workflow_array('fake_context')
        self.assertTrue(len(self.workflow_manager.workflows) == 0)

    def test_empty_auto_locator(self):
        self.workflow_manager.auto_find_workflow_directories()
        self.assertEqual(0, len(self.workflow_manager.auto_found_workflow_dirs))
