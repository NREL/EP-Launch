import time

from eplaunch.workflows.base import BaseEPLaunch3Workflow, EPLaunch3WorkflowResponse


class ColumnNames(object):
    Errors = 'Errors [-]'
    FloorArea = 'Floor Area [m2]'
    EUI = 'EUI [J]'


class EnergyPlusWorkflowSI(BaseEPLaunch3Workflow):

    def name(self):
        return "EnergyPlus SI"

    def description(self):
        return "Run EnergyPlus with SI unit system"

    def get_file_types(self):
        return ["*.idf", "*.imf"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def get_interface_columns(self):
        return [ColumnNames.Errors, ColumnNames.FloorArea, ColumnNames.EUI]

    def main(self, file_path, args):
        column_data = {}
        for i in range(5):
            time.sleep(1)
            if self.abort:
                return EPLaunch3WorkflowResponse(
                    success=False,
                    message="Abort command accepted!",
                    column_data=column_data
                )
        column_data = {ColumnNames.Errors: 0, ColumnNames.FloorArea: 2000, ColumnNames.EUI: 5.0}
        return EPLaunch3WorkflowResponse(
            success=True,
            message="Ran EnergyPlus OK for file: %s!" % file_path,
            column_data=column_data
        )


class EnergyPlusWorkflowIP(BaseEPLaunch3Workflow):

    def name(self):
        return "EnergyPlus IP"

    def description(self):
        return "Run EnergyPlus with IP unit system"

    def get_file_types(self):
        return ["*.idf", "*.imf"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def main(self, file_path, args):
        pass
