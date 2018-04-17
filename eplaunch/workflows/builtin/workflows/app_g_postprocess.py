from eplaunch.workflows.base import BaseWorkflow


class AppGPostProcessWorkflow(BaseWorkflow):

    def name(self):
        return "AppGPostProcess"

    def description(self):
        return "Run Appendix G Post-processor"

    def get_file_types(self):
        return ["*.html"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}
