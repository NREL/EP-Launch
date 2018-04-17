import time

from eplaunch.workflows.base import BaseEPLaunch3Workflow, EPLaunch3WorkflowResponse


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
        return ['Errors [-]', 'Floor Area [m2]', 'EUI [J]']

    def main(self, args):
        for i in range(5):
            time.sleep(1)
            if self.abort:
                return EPLaunch3WorkflowResponse(success=False, message="Abort command accepted!")
        return EPLaunch3WorkflowResponse(success=True, message="Ran EnergyPlus OK!")


class EnergyPlusWorkflowIP(BaseEPLaunch3Workflow):

    def name(self):
        return "EnergyPlus IP"

    def description(self):
        return "Run EnergyPlus with IP unit system"

    def get_file_types(self):
        return ["*.idf", "*.imf"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def main(self, args):
        pass
