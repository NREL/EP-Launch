import os
import subprocess
import platform
import time

from eplaunch.workflows.base import BaseEPLaunch3Workflow, EPLaunch3WorkflowResponse
from eplaunch.utilities.version import Version


class ColumnNames(object):
    Errors = 'Errors'
    Warnings = 'Warnings'
    Runtime = 'Runtime [s]'
    Version = 'Version'


class EPlusRunManager(object):
    # This will eventually be a path relative to this script.
    # Since these workflows will live at /EnergyPlus/Install/workflows/energyplus.py
    # We will generate the path dynamically from __file__ and os.path.join to get to the E+ binary
    if platform.system() == 'Windows':
        EnergyPlusBinary = 'c:\\EnergyPlusV8-9-0\\energyplus.exe'
    else:
        EnergyPlusBinary = '/home/edwin/Programs/EnergyPlus-8-9-0/energyplus'

    @staticmethod
    def get_end_summary(end_file_path):
        contents = open(end_file_path, 'r').read()
        if 'EnergyPlus Completed Successfully' not in contents:
            return False, None, None, None
        last_line_tokens = contents.split(' ')
        num_warnings = int(last_line_tokens[3])
        num_errors = int(last_line_tokens[5])
        time_position_marker = contents.index('Time=')
        time_string = contents[time_position_marker:]
        num_hours = int(time_string[5:7])
        num_minutes = int(time_string[10:12])
        num_seconds = float(time_string[16:21])
        runtime_seconds = num_seconds + num_minutes / 60 + num_hours / 3600
        return True, num_errors, num_warnings, runtime_seconds

    @staticmethod
    def eplus_suffixes():
        suffixes = list()
        # the following are in the same order as the buttons in EP-Launch 2
        suffixes.append("Table.htm")
        suffixes.append(".csv")
        suffixes.append("Meter.csv")

        suffixes.append(".err")
        suffixes.append(".rdd")
        suffixes.append(".mdd")

        suffixes.append(".eio")
        suffixes.append(".svg")
        suffixes.append(".dxf")

        suffixes.append(".mtd")
        suffixes.append("Zsz.csv")
        suffixes.append("Ssz.csv")

        suffixes.append("DElight.in")
        suffixes.append("DElight.out")
        suffixes.append("Map.csv")

        suffixes.append("DElight.eldmp")
        suffixes.append("DElight.dfdmp")
        suffixes.append("Screen.csv")

        suffixes.append(".expidf")
        suffixes.append(".epmidf")
        suffixes.append(".epmdet")

        suffixes.append(".shd")
        suffixes.append(".wrl")
        suffixes.append(".audit")

        suffixes.append(".bnd")
        suffixes.append(".dbg")
        suffixes.append(".sln")

        suffixes.append("_bsmt.out")
        suffixes.append(".bsmt")
        suffixes.append("_bsmt.audit")

        suffixes.append(".eso")
        suffixes.append(".mtr")
        suffixes.append("Proc.csv")

        suffixes.append("_slab.out")
        suffixes.append(".slab")
        suffixes.append("_slab.ger")

        suffixes.append("_bsmt.csv")
        suffixes.append(".edd")
        suffixes.append("Table.xml")

        # the following were not included in EP-Launch 2
        suffixes.append(".end")
        suffixes.append(".sci")
        suffixes.append(".rvaudit")
        suffixes.append(".sql")
        suffixes.append(".log")

        # the rest of these are alternative extensions for the same
        suffixes.append("Table.csv")
        suffixes.append("Table.tab")
        suffixes.append("Table.txt")

        suffixes.append(".tab")
        suffixes.append(".txt")

        suffixes.append("Meter.tab")
        suffixes.append("Meter.txt")

        suffixes.append("Zsz.tab")
        suffixes.append("Zsz.txt")
        suffixes.append("Ssz.tab")
        suffixes.append("Ssz.txt")

        suffixes.append("Map.tab")
        suffixes.append("Map.txt")
        return suffixes


class EnergyPlusWorkflowSI(BaseEPLaunch3Workflow):

    def name(self):
        return "EnergyPlus 8.9 SI"

    def description(self):
        return "Run EnergyPlus with SI unit system"

    def get_file_types(self):
        return ["*.idf", "*.imf"]

    def get_output_suffixes(self):
        return EPlusRunManager.eplus_suffixes()

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def get_interface_columns(self):
        return [ColumnNames.Errors, ColumnNames.Warnings, ColumnNames.Runtime, ColumnNames.Version]

    def main(self, run_directory, file_name, args):
        full_file_path = os.path.join(run_directory, file_name)
        file_name_no_ext, extension = os.path.splitext(file_name)

        v = Version()
        is_found, current_version, numeric_version = v.check_energyplus_version(full_file_path)
        if is_found:
            if numeric_version >= 80900:

                # start with the binary name, obviously
                command_line_args = [EPlusRunManager.EnergyPlusBinary]

                # need to run readvars
                command_line_args += ['--readvars']

                # add some config parameters
                command_line_args += ['--output-prefix', file_name_no_ext, '--output-suffix', 'C']

                # add in simulation control args
                if 'weather' in args and args['weather']:
                    command_line_args += ['--weather', args['weather']]
                else:
                    command_line_args += ['--design-day']

                # and at the very end, add the file to run
                command_line_args += [file_name]

                # run E+ and gather (for now fake) data
                process = subprocess.run(
                    command_line_args,
                    cwd=run_directory
                )
                time.sleep(5)
                status_code = process.returncode

                if status_code != 0:
                    return EPLaunch3WorkflowResponse(
                        success=False,
                        message="EnergyPlus failed for file: %s!" % full_file_path,
                        column_data={}
                    )

                end_file_name = "{0}.end".format(file_name_no_ext)
                end_file_path = os.path.join(run_directory, end_file_name)
                success, errors, warnings, runtime = EPlusRunManager.get_end_summary(end_file_path)

                column_data = {ColumnNames.Errors: errors, ColumnNames.Warnings: warnings, ColumnNames.Runtime: runtime, ColumnNames.Version: current_version}

                # now leave
                return EPLaunch3WorkflowResponse(
                    success=True,
                    message="Ran EnergyPlus OK for file: %s!" % file_name,
                    column_data=column_data
                )

        else:

            errors = "wrong version"
            column_data = {ColumnNames.Errors: errors, ColumnNames.Warnings: '', ColumnNames.Runtime: 0, ColumnNames.Version: current_version}

            # now leave
            return EPLaunch3WorkflowResponse(
                success=False,
                message="Incorrect Version found {}: {}!".format(current_version, file_name),
                column_data=column_data
            )


class EnergyPlusWorkflowIP(BaseEPLaunch3Workflow):

    def name(self):
        return "EnergyPlus 8.9 IP"

    def description(self):
        return "Run EnergyPlus with IP unit system"

    def get_file_types(self):
        return ["*.idf", "*.imf"]

    def get_output_suffixes(self):
        return EPlusRunManager.eplus_suffixes()

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def get_interface_columns(self):
        return [ColumnNames.Errors, ColumnNames.Warnings, ColumnNames.Runtime, ColumnNames.Version]

    def main(self, run_directory, file_name, args):
        full_file_path = os.path.join(run_directory, file_name)
        file_name_no_ext, extension = os.path.splitext(file_name)

        v = Version()
        is_found, current_version, numeric_version = v.check_energyplus_version(full_file_path)
        if is_found:
            if numeric_version >= 80900:

                # run E+ and gather (for now fake) data
                process = subprocess.run(
                    [
                        EPlusRunManager.EnergyPlusBinary, '--output-prefix', file_name_no_ext, '--design-day', file_name
                    ],
                    cwd=run_directory
                )
                status_code = process.returncode

                if status_code != 0:
                    return EPLaunch3WorkflowResponse(
                        success=False,
                        message="EnergyPlus failed for file: %s!" % full_file_path,
                        column_data={}
                    )

                end_file_name = "{0}out.end".format(file_name_no_ext)
                end_file_path = os.path.join(run_directory, end_file_name)
                success, errors, warnings, runtime = EPlusRunManager.get_end_summary(end_file_path)

                column_data = {ColumnNames.Errors: errors, ColumnNames.Warnings: warnings, ColumnNames.Runtime: runtime, ColumnNames.Version: current_version}

                # now leave
                return EPLaunch3WorkflowResponse(
                    success=True,
                    message="Ran EnergyPlus OK for file: %s!" % file_name,
                    column_data=column_data
                )

        else:

            errors = "wrong version"
            column_data = {ColumnNames.Errors: errors, ColumnNames.Warnings: '', ColumnNames.Runtime: 0, ColumnNames.Version: current_version}

            # now leave
            return EPLaunch3WorkflowResponse(
                success=False,
                message="Incorrect Version found {}: {}!".format(current_version, file_name),
                column_data=column_data
            )
