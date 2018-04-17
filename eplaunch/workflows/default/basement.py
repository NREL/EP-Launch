from eplaunch.workflows.base import BaseEPLaunch3Workflow


class BasementWorkflow(BaseEPLaunch3Workflow):

    def name(self):
        return "Basement"

    def description(self):
        return "Run Baement Pre-processor"

    def get_file_types(self):
        return ["*.idf"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def main(self, args):
        pass
