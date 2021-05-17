import unittest

from eplaunch.workflows.base import EPLaunchWorkflowResponse1, BaseEPLaunchWorkflow1


class TestWorkflowResponseConstruction(unittest.TestCase):

    def test_proper_construction(self):
        wfr = EPLaunchWorkflowResponse1(True, 'It is done', {'column1': 'data1'}, extra='data')
        self.assertTrue(wfr.success)
        self.assertEqual(wfr.message, 'It is done')
        self.assertIn('column1', wfr.column_data)
        self.assertIn('extra', wfr.extra_data)


class TestBaseWorkflowMethods(unittest.TestCase):

    def setUp(self):
        self.base_workflow = BaseEPLaunchWorkflow1()

    def test_name_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.name()

    def test_context_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.context()

    def test_description_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.description()

    def test_get_file_types_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.get_file_types()

    def test_get_output_suffixes_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.get_output_suffixes()

    def test_get_extra_data_optional(self):
        self.base_workflow.get_extra_data()

    def test_get_interface_columns_optional(self):
        self.base_workflow.get_interface_columns()

    def test_main_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.main('run_dir', 'file_name', ['arg1'])


class TestBaseWorkflowFunctionality(unittest.TestCase):
    class MyFakeWorkflow(BaseEPLaunchWorkflow1):
        def name(self):
            pass

        def context(self):
            pass

        def description(self):
            pass

        def get_file_types(self):
            pass

        def get_output_suffixes(self):
            pass

        def main(self, run_directory, file_name, args):
            self.callback("Hello")
            # I don't quite understand why but Python is skipping over this in getting coverage as well as
            # in the debugger.  I can step into the base class callback() function call just above, but when I step
            # into this next line it just acts like nothing happens.  I can run all the workflows from the GUI though
            # so I know this is generally working fine.  I'm not really sure.
            self.execute_for_callback(['sleep', '1'], '/')

    def setUp(self):
        self.workflow = TestBaseWorkflowFunctionality.MyFakeWorkflow()

    @staticmethod
    def callback(my_id, msg):
        pass

    def test_run_fake_workflow(self):
        self.workflow.name()
        self.workflow.context()
        self.workflow.description()
        self.workflow.get_file_types()
        self.workflow.get_output_suffixes()
        self.workflow.register_standard_output_callback(
            0,
            TestBaseWorkflowFunctionality.callback
        )
        self.workflow.main(".", "", [])
        self.workflow.abort()
