from eplaunch.workflows.base import BaseWorkflow


class EnergyPlusWorkflowSI(BaseWorkflow):

    def name(self):
        return "EnergyPlus SI"

    def description(self):
        return "Run EnergyPlus with SI unit system"

    def get_file_types(self):
        return ["*.idf", "*.imf"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}


class EnergyPlusWorkflowIP(BaseWorkflow):

    def name(self):
        return "EnergyPlus IP"

    def description(self):
        return "Run EnergyPlus with IP unit system"

    def get_file_types(self):
        return ["*.idf", "*.imf"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}
