import os
import shutil
import subprocess
import platform

from eplaunch.workflows.base import BaseEPLaunch3Workflow, EPLaunch3WorkflowResponse


class CoeffCheckWorkflow(BaseEPLaunch3Workflow):

    def name(self):
        return "CoeffCheck"

    def description(self):
        return "Run Coeff Check"

    def get_file_types(self):
        return ["*.cci"]

    def get_output_suffixes(self):
        return [".cco"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def get_interface_columns(self):
        return []

    def main(self, run_directory, file_name, args):
        if platform.system() == 'Windows':
            coeffcheck_binary = 'c:\\EnergyPlusV8-9-0\\PreProcess\\CoeffConv\\CoeffCheck.exe'
        else:
            coeffcheck_binary = '/home/edwin/Programs/EnergyPlus-8-9-0/Preprocess/CoeffConv/CoeffCheck'

        cci_file_with_path = os.path.join(run_directory, file_name)
        cci_file_no_ext, _ = os.path.splitext(cci_file_with_path)
        cco_file_with_path = cci_file_no_ext + '.cco'

        # clean up working directory
        cc_input_txt_file = os.path.join(run_directory, 'CoeffCheckInput.txt')
        if os.path.exists(cc_input_txt_file):
            os.remove(cc_input_txt_file)
        cc_output_txt_file = os.path.join(run_directory, 'CoeffCheckOutput.txt')
        if os.path.exists(cc_output_txt_file):
            os.remove(cc_output_txt_file)

        # copy input data file to working directory
        if os.path.exists(cci_file_with_path) and os.path.exists(coeffcheck_binary) and os.path.exists(run_directory):
            shutil.copy2(cci_file_with_path, cc_input_txt_file)

            # execute utility
            command_line_args = [coeffcheck_binary, ]
            process = subprocess.run(
                command_line_args,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=run_directory
            )
            if process.returncode == 0:
                # Remove old version of the output file
                if os.path.exists(cco_file_with_path):
                    os.remove(cco_file_with_path)

                # Copy output files to input/output path
                shutil.copy2(cc_output_txt_file, cco_file_with_path)

                # Clean up directory.
                if os.path.exists(cc_input_txt_file):
                    os.remove(cc_input_txt_file)
                if os.path.exists(cc_output_txt_file):
                    os.remove(cc_output_txt_file)

                return EPLaunch3WorkflowResponse(
                    success=True,
                    message="Ran CoeffCheck OK for file: {}!".format(cci_file_with_path),
                    column_data=[]
                )
            else:
                return EPLaunch3WorkflowResponse(
                    success=False,
                    message="CoeffCheck failed for file: {}!".format(cci_file_with_path),
                    column_data=[]
                )
        else:
            return EPLaunch3WorkflowResponse(
                success=False,
                message="CoeffCheck file not found: {}!".format(cci_file_with_path),
                column_data=[]
            )
