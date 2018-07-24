import os
import shutil
import subprocess
import platform

from eplaunch.workflows.base import BaseEPLaunch3Workflow, EPLaunch3WorkflowResponse


class CoeffConvWorkflow(BaseEPLaunch3Workflow):

    def name(self):
        return "CoeffConv"

    def description(self):
        return "Run CoeffConv"

    def get_file_types(self):
        return ["*.coi"]

    def get_output_suffixes(self):
        return [".coo"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def get_interface_columns(self):
        return []

    def main(self, run_directory, file_name, args):
        if platform.system() == 'Windows':
            coeffconv_binary = 'c:\\EnergyPlusV8-9-0\\PreProcess\\CoeffConv\\CoeffConv.exe'
        else:
            coeffconv_binary = '/home/edwin/Programs/EnergyPlus-8-9-0/Preprocess/CoeffConv/CoeffConv'

        coi_file_with_path = os.path.join(run_directory, file_name)
        coi_file_no_ext, _ = os.path.splitext(coi_file_with_path)
        coo_file_with_path = coi_file_no_ext + '.coo'

        # clean up working directory
        cc_input_txt_file = os.path.join(run_directory, 'CoeffConvInput.txt')
        if os.path.exists(cc_input_txt_file):
            os.remove(cc_input_txt_file)
        cc_output_txt_file = os.path.join(run_directory, 'CoeffConvOutput.txt')
        if os.path.exists(cc_output_txt_file):
            os.remove(cc_output_txt_file)

        # copy input data file to working directory
        if os.path.exists(coi_file_with_path) and os.path.exists(coeffconv_binary) and os.path.exists(run_directory):
            shutil.copy2(coi_file_with_path, cc_input_txt_file)

            # execute utility
            command_line_args = [coeffconv_binary, ]
            process = subprocess.run(
                command_line_args,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=run_directory
            )
            if process.returncode == 0:
                # Remove old version of the output file
                if os.path.exists(coo_file_with_path):
                    os.remove(coo_file_with_path)

                # Copy output files to input/output path
                shutil.copy2(cc_output_txt_file, coo_file_with_path)

                # Clean up directory.
                if os.path.exists(cc_input_txt_file):
                    os.remove(cc_input_txt_file)
                if os.path.exists(cc_output_txt_file):
                    os.remove(cc_output_txt_file)

                return EPLaunch3WorkflowResponse(
                    success=True,
                    message="Ran CoeffConv OK for file: {}!".format(coi_file_with_path),
                    column_data=[]
                )
            else:
                return EPLaunch3WorkflowResponse(
                    success=False,
                    message="CoeffConv failed for file: {}!".format(coi_file_with_path),
                    column_data=[]
                )
        else:
            return EPLaunch3WorkflowResponse(
                success=False,
                message="CoeffConv file not found: {}!".format(coi_file_with_path),
                column_data=[]
            )
