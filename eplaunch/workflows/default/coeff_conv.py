from eplaunch.workflows.base import BaseEPLaunch3Workflow


class CoeffConvWorkflow(BaseEPLaunch3Workflow):

    def name(self):
        return "CoeffConv"

    def description(self):
        return "Run CoeffConv"

    def get_file_types(self):
        return ["*.coi"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def main(self, run_directory, file_name, args):
        pass
