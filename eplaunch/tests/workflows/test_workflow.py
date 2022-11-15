from pathlib import Path
from unittest import TestCase

from eplaunch.workflows.workflow import Workflow
from eplaunch.workflows.workflow_tester import main as tester


class TestWorkflow(TestCase):
    def test_workflow_exists(self):
        w = Workflow(
            None, 'name', 'context', ['txt, idf'], ['file_types'], ['size', 'warnings'],
            Path('/workflow/dir'), 'description', is_energyplus=False, uses_weather=True, version_id=1
        )
        self.assertIsInstance(str(w), str)
        pass


class TestDefaultWorkflows(TestCase):
    def setUp(self) -> None:
        self.default_workflow_dir = Path(__file__).resolve().parent.parent.parent / 'workflows' / 'default'

    def test_file_details(self):
        workflow_file = self.default_workflow_dir / 'file_details.py'
        self.assertEqual(0, tester(str(workflow_file)))

    def test_idf_details(self):
        workflow_file = self.default_workflow_dir / 'idf_details.py'
        self.assertEqual(0, tester(str(workflow_file)))

    def test_site_location(self):
        workflow_file = self.default_workflow_dir / 'site_location.py'
        self.assertEqual(0, tester(str(workflow_file)))
