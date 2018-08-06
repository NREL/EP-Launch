from importlib import util as import_util
import inspect
import os


class WorkflowDetail:
    def __init__(self, workflow_instance, description, is_energyplus, version_id):
        self.workflow_instance = workflow_instance
        self.description = description
        self.is_energyplus = is_energyplus
        self.version_id = version_id


def get_workflows(external_workflow_directories):
    this_file_directory_path = os.path.dirname(os.path.realpath(__file__))
    built_in_workflow_directory = os.path.join(this_file_directory_path, 'default')
    all_workflow_directories = external_workflow_directories
    if built_in_workflow_directory not in all_workflow_directories:
        all_workflow_directories.append(built_in_workflow_directory)

    work_flows = []
    print("Found workflow directories: ")
    print(all_workflow_directories)

    for workflow_directory in all_workflow_directories:
        uc_directory = workflow_directory.upper().replace('-', '.').replace('\\', '/')
        version_id = None
        dir_is_eplus = False
        # I tried regexes and they worked using online Python regex testers, but using the same (copy/pasted) patterns
        # and strings in here resulting in false responses...bogus.  So here I go, manually chopping up a string
        # re_dots = re.compile('(?P<version>(\d.\d.\d))')
        if 'ENERGYPLUS.' in uc_directory:
            dir_is_eplus = True
            trailing_string = uc_directory[uc_directory.index('ENERGYPLUS.') + 11:]
            if '/' in trailing_string:
                version_id = trailing_string[:trailing_string.index('/')]

        modules = []
        for this_file in os.listdir(workflow_directory):
            if not this_file.endswith('py'):
                continue
            if '__init__.py' in this_file:
                continue
            this_file_path = os.path.join(workflow_directory, this_file)
            module_spec = import_util.spec_from_file_location('workflow_module', this_file_path)
            this_module = import_util.module_from_spec(module_spec)
            modules.append(this_module)
            module_spec.loader.exec_module(this_module)

        for this_module in modules:
            class_members = inspect.getmembers(this_module, inspect.isclass)
            for this_class in class_members:
                this_class_name, this_class_type = this_class
                # so right here, we could check issubclass, but this would also match the BaseEPLaunch3Workflow, which
                # is imported in each workflow class.  No need to do that.  For now I'm going to check the direct
                # parent class of this class to verify we only get direct descendants.  We can evaluate this later.
                # if issubclass(this_class_type, BaseEPLaunch3Workflow):
                num_inheritance = len(this_class_type.__bases__)
                base_class_name = this_class_type.__bases__[0].__name__
                workflow_base_class_name = 'BaseEPLaunch3Workflow'
                if num_inheritance == 1 and workflow_base_class_name in base_class_name:
                    # we've got a good match, grab a bit more data and get ready to load this into the Detail class
                    workflow_instance = this_class_type()
                    workflow_name = workflow_instance.name()
                    workflow_file_types = workflow_instance.get_file_types()

                    file_type_string = "("
                    first = True
                    for file_type in workflow_file_types:
                        if first:
                            first = False
                        else:
                            file_type_string += ", "
                        file_type_string += file_type
                    file_type_string += ")"

                    description = "%s %s" % (workflow_name, file_type_string)

                    if dir_is_eplus and version_id:
                        description += ' (E+ v%s)' % version_id
                    elif built_in_workflow_directory == workflow_directory:
                        description += ' (builtin)'

                    work_flows.append(WorkflowDetail(
                        workflow_instance,
                        description,
                        dir_is_eplus,
                        version_id
                    ))

    work_flows.sort(key=lambda w: w.description)
    return work_flows
