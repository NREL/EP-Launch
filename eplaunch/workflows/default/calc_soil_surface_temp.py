from eplaunch.workflows.base import BaseEPLaunch3Workflow


class CalcSoilSurfTempWorkflow(BaseEPLaunch3Workflow):

    def name(self):
        return "CalcSoilSurfTemp"

    def description(self):
        return "Run CalcSoilSurfTemp Preprocessor"

    def get_file_types(self):
        return ["*.epw"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}
