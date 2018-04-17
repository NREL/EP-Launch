from eplaunch.workflows.base import BaseEPLaunch3Workflow


class AppGPostProcessWorkflow(BaseEPLaunch3Workflow):

    def name(self):
        return "AppGPostProcess"

    def description(self):
        return "Run Appendix G Post-processor"

    def get_file_types(self):
        return ["*.html"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def get_interface_columns(self):
        return ['AppG Errors [-]', 'AppG Something [-]']

    def main(self):
        pass
