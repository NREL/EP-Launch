# import importlib
from importlib import util as import_util
import inspect
import os
import re


def get_workflows(workflow_path=None):
    this_file_directory_path = os.path.dirname(os.path.realpath(__file__))
    built_in_workflow_directory = os.path.join(this_file_directory_path, 'default')

    if not workflow_path:
        workflow_path = built_in_workflow_directory

    py_search_regex = re.compile('.py$', re.IGNORECASE)
    workflow_files = filter(py_search_regex.search, os.listdir(workflow_path))

    modules = []
    for this_file in workflow_files:
        if '__init__.py' in this_file:
            continue
        this_file_path = os.path.join(workflow_path, this_file)
        module_spec = import_util.spec_from_file_location('workflow_module', this_file_path)
        module = import_util.module_from_spec(module_spec)
        modules.append(module)
        module_spec.loader.exec_module(module)

    workflow_classes = []
    for this_module in modules:
        class_members = inspect.getmembers(this_module, inspect.isclass)
        for this_class in class_members:
            this_class_name, this_class_type = this_class
            # so right here, we could check the issubclass, but this will also match for the BaseEPLaunch3Workflow, which
            # is likely imported in each workflow class.  No need to do that.  For now I'm going to check the direct
            # parent class of this class to verify we only get direct descendants.  We can evaluate this later.
            # if issubclass(this_class_type, BaseEPLaunch3Workflow):
            num_inheritance = len(this_class_type.__bases__)
            base_class_name = this_class_type.__bases__[0].__name__
            workflow_base_class_name = 'BaseEPLaunch3Workflow'
            if num_inheritance == 1 and workflow_base_class_name in base_class_name:
                workflow_classes.append(this_class_type)

    workflow_classes.sort(key=lambda w: w.__name__)
    return workflow_classes
