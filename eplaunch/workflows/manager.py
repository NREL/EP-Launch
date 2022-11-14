from pathlib import Path
from string import ascii_uppercase
from typing import Dict, List, Optional
from importlib import util as import_util
from inspect import getmembers, isclass

from eplaunch.utilities.crossplatform import Platform
from eplaunch.workflows.workflow import Workflow


class WorkflowManager:
    def __init__(self):
        self.current_workflow: Optional[Workflow] = None
        self.threads = {}
        self.workflow_directories: List[Path] = []
        self.auto_found_workflow_dirs: List[Path] = []
        self.workflows: List[Workflow] = []
        self.workflow_contexts = set()

    def workflow_instances(self, workflow_context: str) -> List:
        return [x for x in self.workflows if x.context == workflow_context]

    def locate_all_workflows(self):
        self.auto_found_workflow_dirs = []   # Path('/eplus/installs/EnergyPlus-22-1-0/workflows')]
        # then search for e+ workflows
        search_roots: Dict[str, List[Path]] = {
            Platform.WINDOWS: [Path(f"{c}:\\") for c in ascii_uppercase],
            Platform.LINUX: [Path('/usr/local/bin/'), Path('/tmp/')],
            Platform.MAC: [Path('/Applications/'), Path('/tmp/')],
            Platform.UNKNOWN: [],
        }
        current_search_roots = search_roots[Platform.get_current_platform()]
        search_names = ["EnergyPlus*", "energyplus*", "EP*", "ep*", "E+*", "e+*"]
        for search_root in current_search_roots:
            for search_name in search_names:
                eplus_folder_matches = search_root.glob(search_name)
                for ep_folder in eplus_folder_matches:  # pragma: no cover, would have to install into system folders
                    ep_workflow_dir = ep_folder / 'workflows'
                    if ep_workflow_dir.exists():
                        self.auto_found_workflow_dirs.append(ep_workflow_dir)

    def instantiate_all_workflows(
            self, disable_builtins=False, skip_error: bool = False, extra_workflow_dir: Optional[Path] = None) -> str:
        this_file_directory_path = Path(__file__).parent.resolve()
        this_project_root_dir = this_file_directory_path.parent
        built_in_workflow_dir = this_project_root_dir / 'workflows' / 'default'
        all_workflow_directories = self.workflow_directories
        if disable_builtins:
            # don't add built-in default workflows
            pass
        elif built_in_workflow_dir not in all_workflow_directories and built_in_workflow_dir.exists():
            # add the built-in directory if it exists
            all_workflow_directories.append(built_in_workflow_dir)
        if extra_workflow_dir is not None:
            all_workflow_directories.append(extra_workflow_dir)

        self.workflows = []
        self.workflow_contexts.clear()
        warnings = []
        for i, workflow_directory in enumerate(all_workflow_directories):
            sanitized_directory_upper_case = str(workflow_directory).upper().replace('-', '.').replace('\\', '/')
            version_id = None
            dir_is_eplus = False
            # I tried regexes, and they worked using online Python regex testers, but using the same patterns
            # and strings in here resulting in false responses...bogus.  So here I go, manually chopping up a string
            # re_dots = re.compile('(?P<version>(\d.\d.\d))')
            if Platform.get_current_platform() == Platform.WINDOWS:  # pragma: no cover, skipping platform specifics
                energyplus_uc_search_string = 'ENERGYPLUSV'
            else:  # pragma: no cover, skipping platform specifics
                energyplus_uc_search_string = 'ENERGYPLUS.'
            if energyplus_uc_search_string in sanitized_directory_upper_case:
                dir_is_eplus = True
                san = sanitized_directory_upper_case
                trailing_string = san[san.index(energyplus_uc_search_string) + 11:]
                if '/' in trailing_string:
                    version_id = trailing_string[:trailing_string.index('/')]

            modules = []
            for this_file_path in workflow_directory.glob('*.py'):
                if this_file_path.name == '__init__.py':
                    continue
                module_spec = import_util.spec_from_file_location(('workflow_module_%s' % i), this_file_path)
                this_module = import_util.module_from_spec(module_spec)
                try:
                    modules.append([this_file_path, this_module])
                    module_spec.loader.exec_module(this_module)
                except ImportError as ie:
                    # this error generally means they have a bad workflow class or something
                    warnings.append(
                        f"Import error occurred on workflow file {str(this_file_path)}: {ie.msg}"
                    )
                    continue
                except SyntaxError as se:
                    # syntax errors are, well, syntax errors in the Python code itself
                    warnings.append(
                        f"Syntax error occurred on workflow file {str(this_file_path)}, line {se.lineno}: {se.msg}"
                    )
                    continue
                except Exception as e:  # pragma: no cover
                    # there's always the potential of some other unforeseen thing going on when a workflow is executed
                    warnings.append(
                        f"Unexpected error occurred trying to import workflow: {str(this_file_path)}: {str(e)}"
                    )
                    continue

            for module_file_path, this_module in modules:
                class_members = getmembers(this_module, isclass)
                for this_class in class_members:
                    this_class_name, this_class_type = this_class
                    # so right here, we could check issubclass, but this also matches the BaseEPLaunchWorkflow1, which
                    # is imported in each workflow class.  No need to do that.  For now, I'm going to check the direct
                    # parent class of this class to verify we only get direct descendants.  We can evaluate this later.
                    # if issubclass(this_class_type, BaseEPLaunchWorkflow1):
                    num_inheritance = len(this_class_type.__bases__)
                    base_class_name = this_class_type.__bases__[0].__name__
                    workflow_base_class_name = 'BaseEPLaunchWorkflow1'
                    if num_inheritance == 1 and workflow_base_class_name in base_class_name:
                        try:
                            # we've got a good match, grab more data and get ready to load this into the Detail class
                            workflow_instance = this_class_type()
                            workflow_name = workflow_instance.name()
                            workflow_file_types = workflow_instance.get_file_types()
                            workflow_output_suffixes = workflow_instance.get_output_suffixes()
                            workflow_columns = workflow_instance.get_interface_columns()
                            workflow_context = workflow_instance.context()
                            workflow_weather = workflow_instance.uses_weather()

                            file_type_string = "("
                            first = True
                            for file_type in workflow_file_types:
                                if first:
                                    first = False
                                else:
                                    file_type_string += ", "
                                file_type_string += file_type
                            file_type_string += ")"

                            description = f"{workflow_name} {file_type_string}"
                            self.workflow_contexts.add(workflow_context)

                            self.workflows.append(
                                Workflow(
                                    this_class_type,
                                    workflow_name,
                                    workflow_context,
                                    workflow_output_suffixes,
                                    workflow_file_types,
                                    workflow_columns,
                                    workflow_directory,
                                    description,
                                    dir_is_eplus,
                                    workflow_weather,
                                    version_id
                                )
                            )
                        except NotImplementedError as nme:
                            warnings.append(
                                f"Import error for file \"{module_file_path}\"; class: \"{this_class_name}\"; error: "
                                f"\"{str(nme)}\" "
                            )
                        except Exception as e:
                            # there's always the potential of some other thing going on when a workflow is executed
                            warnings.append(
                                f"Unexpected error in file \"{module_file_path}\"; class: \"{this_class_name}\"; error:"
                                f" \"{str(e)}\" "
                            )
                            continue

        self.workflows.sort(key=lambda w: w.description)
        warning_message = ''
        if skip_error:
            pass
        elif len(warnings) > 0:
            warning_message = 'Errors occurred during workflow importing! \n'
            warning_message += 'Address these issues or remove the workflow directory in the settings \n'
            for warning in warnings:
                warning_message += '\n - ' + str(warning)
        return warning_message

    def reset_workflow_array(self, filter_context=None):
        self.instantiate_all_workflows()
        if filter_context:
            self.workflows = [w for w in self.workflows if w.context == filter_context]
