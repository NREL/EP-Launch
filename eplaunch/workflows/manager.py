import inspect
import os
import platform

from importlib import util as import_util


class FailedWorkflowDetails:
    def __init__(self, workflow_file_path, message):
        self.workflow_file_path = workflow_file_path
        self.message = message


class WorkflowDetail:
    def __init__(self, workflow_class, name, context, output_suffixes, file_types, columns,
                 directory, description, is_energyplus, version_id):
        self.workflow_class = workflow_class
        self.name = name
        self.context = context
        self.output_suffixes = output_suffixes
        self.file_types = file_types
        self.columns = columns
        self.workflow_directory = directory
        self.description = description
        self.is_energyplus = is_energyplus
        self.version_id = version_id
        self.output_toolbar_order = None


def get_workflows(external_workflow_directories, disable_builtins=False):

    # until we actually remove the E+ related workflows from the ep-launch repo, we should at least
    # ignore them in the UI so the user isn't confused
    builtin_blacklist = [
        'app_g_postprocess.py',
        'calc_soil_surface_temp.py',
        'coeff_check.py',
        'coeff_conv.py',
        'energyplus.py',
        'transition.py'
    ]

    this_file_directory_path = os.path.dirname(os.path.realpath(__file__))
    built_in_workflow_directory = os.path.join(this_file_directory_path, 'default')
    all_workflow_directories = external_workflow_directories
    if disable_builtins:
        # don't add built-in default workflows
        pass
    elif built_in_workflow_directory not in all_workflow_directories and os.path.exists(built_in_workflow_directory):
        # add the built-in directory if it exists
        all_workflow_directories.add(built_in_workflow_directory)

    work_flows = []
    warnings = []
    for workflow_directory in all_workflow_directories:
        uc_directory = workflow_directory.upper().replace('-', '.').replace('\\', '/')
        version_id = None
        dir_is_eplus = False
        # I tried regexes and they worked using online Python regex testers, but using the same (copy/pasted) patterns
        # and strings in here resulting in false responses...bogus.  So here I go, manually chopping up a string
        # re_dots = re.compile('(?P<version>(\d.\d.\d))')
        if platform.system() == 'Windows':
            energyplus_uc_search_string = 'ENERGYPLUSV'
        else:
            energyplus_uc_search_string = 'ENERGYPLUS.'
        if energyplus_uc_search_string in uc_directory:
            dir_is_eplus = True
            trailing_string = uc_directory[uc_directory.index(energyplus_uc_search_string) + 11:]
            if '/' in trailing_string:
                version_id = trailing_string[:trailing_string.index('/')]

        modules = []
        for this_file in os.listdir(workflow_directory):
            if workflow_directory == built_in_workflow_directory and this_file in builtin_blacklist:
                continue
            if not this_file.endswith('py'):
                continue
            if '__init__.py' in this_file:
                continue
            this_file_path = os.path.join(workflow_directory, this_file)
            module_spec = import_util.spec_from_file_location('workflow_module', this_file_path)
            this_module = import_util.module_from_spec(module_spec)
            try:
                modules.append(this_module)
                module_spec.loader.exec_module(this_module)
            except ImportError as ie:
                # this error generally means they have a bad workflow class or something
                warnings.append(
                    "Import error occurred on workflow file %s: %s" % (this_file_path, ie.msg)
                )
                continue
            except SyntaxError as se:
                # syntax errors are, well, syntax errors in the Python code itself
                warnings.append(
                    "Syntax error occurred on workflow file %s, line %s: %s" % (this_file_path, se.lineno, se.msg)
                )
                continue
            except Exception as e:
                # there's always the potential of some other unforeseen thing going on when a workflow is executed
                warnings.append(
                    "Unexpected error occurred trying to import workflow: %s" % this_file_path
                )
                continue

        for this_module in modules:
            class_members = inspect.getmembers(this_module, inspect.isclass)
            for this_class in class_members:
                this_class_name, this_class_type = this_class
                # so right here, we could check issubclass, but this would also match the BaseEPLaunchWorkflow1, which
                # is imported in each workflow class.  No need to do that.  For now I'm going to check the direct
                # parent class of this class to verify we only get direct descendants.  We can evaluate this later.
                # if issubclass(this_class_type, BaseEPLaunchWorkflow1):
                num_inheritance = len(this_class_type.__bases__)
                base_class_name = this_class_type.__bases__[0].__name__
                workflow_base_class_name = 'BaseEPLaunchWorkflow1'
                if num_inheritance == 1 and workflow_base_class_name in base_class_name:
                    # we've got a good match, grab a bit more data and get ready to load this into the Detail class
                    workflow_instance = this_class_type()
                    workflow_name = workflow_instance.name()
                    workflow_file_types = workflow_instance.get_file_types()
                    workflow_output_suffixes = workflow_instance.get_output_suffixes()
                    workflow_columns = workflow_instance.get_interface_columns()
                    workflow_context = workflow_instance.context()

                    file_type_string = "("
                    first = True
                    for file_type in workflow_file_types:
                        if first:
                            first = False
                        else:
                            file_type_string += ", "
                        file_type_string += file_type
                    file_type_string += ")"

                    description = "%s: %s %s" % (workflow_context, workflow_name, file_type_string)

                    work_flows.append(
                        WorkflowDetail(
                            this_class_type,
                            workflow_name,
                            workflow_context,
                            workflow_output_suffixes,
                            workflow_file_types,
                            workflow_columns,
                            workflow_directory,
                            description,
                            dir_is_eplus,
                            version_id
                        )
                    )

    work_flows.sort(key=lambda w: w.description)
    return work_flows, warnings
