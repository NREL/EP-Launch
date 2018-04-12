from eplaunch.workflows.base import BaseWorkflow


class AppGPostProcessWorkflowSI(BaseWorkflow):

    def name(self):
        return "AppGPostProcess"

    def description(self):
        return "Run Appendix G Post-processor"

    def entry_point(self):
        return "Hey it's AppG entry point!"

    def get_file_types(self):
        return ["*.html"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}
