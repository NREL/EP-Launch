import importlib
import inspect
import os
import re


def get_workflows(workflow_path=None):
    this_file_directory_path = os.path.dirname(os.path.realpath(__file__))
    built_in_workflow_directory = os.path.join(this_file_directory_path, 'builtin', 'workflows')

    if not workflow_path:
        workflow_path = built_in_workflow_directory

    py_search_regex = re.compile('.py$', re.IGNORECASE)
    workflow_files = filter(py_search_regex.search, os.listdir(workflow_path))

    def form_module(fp):
        return '.' + os.path.splitext(fp)[0]

    workflows = map(form_module, workflow_files)
    # import parent module / namespace
    importlib.import_module('eplaunch.interface.workflows.builtin.workflows')
    modules = []
    for workflow in workflows:
        if '__init__' in workflow:
            continue
        if not workflow.startswith('__'):
            modules.append(importlib.import_module(workflow, package="eplaunch.interface.workflows.builtin.workflows"))

    workflow_classes = []
    for this_module in modules:
        class_members = inspect.getmembers(this_module, inspect.isclass)
        for this_class in class_members:
            this_class_name, this_class_type = this_class
            # so right here, we could check the issubclass, but this will also match for the BaseWorkflow, which
            # is likely imported in each workflow class.  No need to do that.  For now I'm going to check the direct
            # parent class of this class to verify we only get direct descendants.  We can evaluate this later.
            # if issubclass(this_class_type, BaseWorkflow):
            num_inheritance = len(this_class_type.__bases__)
            base_class_name = this_class_type.__bases__[0].__name__
            workflow_base_class_name = 'BaseWorkflow'
            if num_inheritance == 1 and workflow_base_class_name in base_class_name:
                workflow_classes.append(this_class_type)
    return workflow_classes
