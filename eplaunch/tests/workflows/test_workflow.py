# eplaunch/workflows/workflow.py:Workflow is really just a dataclass, so not much to test, just ensure it is there
from pathlib import Path
from unittest import TestCase

from eplaunch.workflows.workflow import Workflow


class TestWorkflow(TestCase):
    def test_workflow_exists(self):
        w = Workflow(
            None, 'name', 'context', ['txt, idf'], ['file_types'], ['size', 'warnings'],
            Path('/workflow/dir'), 'description', is_energyplus=False, uses_weather=True, version_id=1
        )
        self.assertIsInstance(str(w), str)
        pass
