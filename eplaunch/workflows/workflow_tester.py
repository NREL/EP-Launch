#!/usr/bin/env python

"""
This file is a standalone EP-Launch workflow tester.
It is called using a single argument, the path to a workflow file
"""

import inspect
import os
import sys
from importlib import util as import_util


class WorkflowTesting(object):

    def __init__(self, verbose: bool):
        self.verbose = verbose

    def printer(self, message: str):
        if self.verbose:  # pragma: no cover
            print(message)

    def workflow_file_tester(self, file_path):
        modules = []

        if os.path.exists(file_path):
            self.printer("   OK: File path exists at: " + file_path)
        else:  # pragma: no cover
            print("ERROR: File path does not exist!  Path: " + file_path)
            return 1

        if file_path.endswith('.py'):
            self.printer("   OK: File ends with .py")
        else:  # pragma: no cover
            print("ERROR: File path does NOT end with .py")
            return 1

        module_spec = import_util.spec_from_file_location('workflow_module', file_path)
        this_module = import_util.module_from_spec(module_spec)
        try:
            modules.append(this_module)
            module_spec.loader.exec_module(this_module)
            self.printer("   OK: Python import process completed successfully!")
        except ImportError as ie:  # pragma: no cover
            # this error generally means they have a bad workflow class or something
            print("ERROR: Import error occurred on workflow file %s: %s" % (file_path, ie.msg))
            return 1
        except SyntaxError as se:  # pragma: no cover
            # syntax errors are, well, syntax errors in the Python code itself
            print("ERROR: Syntax error occurred on workflow file %s, line %s: %s" % (file_path, se.lineno, se.msg))
            return 1
        except Exception as e:  # pragma: no cover
            # there's always the potential of some other unforeseen thing going on when a workflow is executed
            print("ERROR: Unexpected error occurred trying to import workflow: %s: %a" % file_path, str(e))
            return 1

        successful_classes = []
        for this_module in modules:
            class_members = inspect.getmembers(this_module, inspect.isclass)
            for this_class in class_members:
                this_class_name, this_class_type = this_class
                self.printer(" INFO: Encountered class: \"" + this_class_name + "\", testing now...")
                # so right here, we could check issubclass, but this would also match the BaseEPLaunchWorkflow1, which
                # is imported in each workflow class.  No need to do that.  For now, I'm going to check the direct
                # parent class of this class to verify we only get direct descendants.  We can evaluate this later.
                # if issubclass(this_class_type, BaseEPLaunchWorkflow1):
                num_inheritance = len(this_class_type.__bases__)
                base_class_name = this_class_type.__bases__[0].__name__
                workflow_base_class_name = 'BaseEPLaunchWorkflow1'
                if num_inheritance == 1 and workflow_base_class_name in base_class_name:
                    self.printer("   OK: Basic inheritance checks out OK for class: " + this_class_name)
                    successful_classes.append(this_class_name)

                    try:
                        workflow_instance = this_class_type()
                        self.printer("   OK: Instantiation of derived class works")
                    except Exception as e:  # pragma: no cover
                        print("ERROR: Instantiation of derived class malfunctioning; reason: " + str(e))
                        return 1

                    try:
                        workflow_instance.name()
                        self.printer("   OK: Overridden name() function execution works")
                    except Exception as e:  # pragma: no cover
                        print("ERROR: name() function not overridden, or malfunctioning; reason: " + str(e))
                        return 1

                    try:
                        workflow_instance.description()
                        self.printer("   OK: Overridden description() function execution works")
                    except Exception as e:  # pragma: no cover
                        print("ERROR: description() function not overridden, or malfunctioning; reason: " + str(e))
                        return 1

                    try:
                        workflow_instance.get_file_types()
                        self.printer("   OK: Overridden get_file_types() function execution works")
                    except Exception as e:  # pragma: no cover
                        print("ERROR: get_file_types() function not overridden, or malfunctioning; reason: " + str(e))
                        return 1

                    try:
                        workflow_instance.get_output_suffixes()
                        self.printer("   OK: Overridden get_output_suffixes() function execution works")
                    except Exception as e:  # pragma: no cover
                        print(f"ERROR: get_output_suffixes() function not overridden, or malfunctioning; reason: {e}")
                        return 1

                    try:
                        workflow_instance.get_interface_columns()
                        self.printer("   OK: Overridden get_interface_columns() function execution works")
                    except Exception as e:  # pragma: no cover
                        print(f"ERROR: get_interface_columns() function not overridden, or malfunctioning; reason: {e}")
                        return 1

                    try:
                        workflow_instance.context()
                        self.printer("   OK: Overridden context() function execution works")
                    except Exception as e:  # pragma: no cover
                        print("ERROR: context() function not overridden, or malfunctioning; reason: " + str(e))
                        return 1

                else:
                    self.printer(" INFO: Inheritance does not check out, will continue with other classes in this file")
                    continue

        if len(successful_classes) > 0:
            t = '\n        - '
            class_list = t.join(successful_classes)
            self.printer(f"   OK: Found {len(successful_classes)} successful workflow imports:{t}{class_list}")
            return 0
        else:  # pragma: no cover
            print("ERROR: Did not find ANY successful workflow imports in this file!")
            return 1


def cli():  # pragma: no cover
    if len(sys.argv) != 2:
        print("Bad call to workflow_tester.cli, give one command line argument, the full path to a workflow file")
        return 2
    else:
        return WorkflowTesting(verbose=True).workflow_file_tester(sys.argv[1])


if __name__ == "__main__":  # pragma: no cover
    sys.exit(cli())
