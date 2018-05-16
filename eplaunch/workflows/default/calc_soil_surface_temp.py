import os
from subprocess import Popen, PIPE

from eplaunch.workflows.base import BaseEPLaunch3Workflow, EPLaunch3WorkflowResponse


class ColumnNames(object):
    AverageSurfTemp = 'Avg Surf Temp [C]'
    AmplitudeSurfTemp = 'Amp Surf Temp [C]'
    PhaseConstant = 'Phase Constant [days]'


class CalcSoilSurfTempWorkflow(BaseEPLaunch3Workflow):
    def name(self):
        return "CalcSoilSurfTemp"

    def description(self):
        return "Run CalcSoilSurfTemp Preprocessor"

    def get_file_types(self):
        return ["*.epw"]

    def get_output_suffixes(self):
        return [".txt"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def get_interface_columns(self):
        return [ColumnNames.AverageSurfTemp, ColumnNames.AmplitudeSurfTemp, ColumnNames.PhaseConstant]

    def main(self, run_directory, file_name, args):

        calc_soil_surf_temp = '/home/edwin/Programs/EnergyPlus-8-9-0/PreProcess/CalcSoilSurfTemp/CalcSoilSurfTemp'

        out_file_path = os.path.join(run_directory, 'CalcSoilSurfTemp.out')
        if os.path.exists(out_file_path):
            try:
                os.remove(out_file_path)
            except OSError:
                return EPLaunch3WorkflowResponse(
                    success=False,
                    message="Could not delete prior CalcSoilSurfTemp results file: %s!" % out_file_path,
                    column_data={}
                )

        full_file_path = os.path.join(run_directory, file_name)

        # run E+ and gather (for now fake) data
        p1 = Popen([calc_soil_surf_temp, file_name], stdout=PIPE, stdin=PIPE, cwd=run_directory)
        p1.communicate(input=b'1\n1\n')

        if not os.path.exists(out_file_path):
            return EPLaunch3WorkflowResponse(
                success=False,
                message="CalcSoilSurfTemp failed for file: %s!" % full_file_path,
                column_data={}
            )

        try:
            with open(out_file_path, 'r') as f:
                lines = f.readlines()
                avg_temp = float(lines[1][40:-1])
                amp_temp = float(lines[2][38:-1])
                phase_constant = int(lines[3][42:-1])
                column_data = {
                    ColumnNames.AverageSurfTemp: avg_temp,
                    ColumnNames.AmplitudeSurfTemp: amp_temp,
                    ColumnNames.PhaseConstant: phase_constant
                }
                return EPLaunch3WorkflowResponse(
                    success=True,
                    message="Ran EnergyPlus OK for file: %s!" % file_name,
                    column_data=column_data
                )
        except Exception:  # noqa -- there could be lots of issues here, file existence, file contents, float conversion
            return EPLaunch3WorkflowResponse(
                success=False,
                message="CalcSoilSurfTemp seemed to run, but post processing failed for file: %s!" % full_file_path,
                column_data={}
            )
