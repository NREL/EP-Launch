from eplaunch.workflows.base import BaseWorkflow


class BasementWorkflow(BaseWorkflow):

    def name(self):
        return "Basement"

    def description(self):
        return "Run Baement Pre-processor"

    def get_file_types(self):
        return ["*.idf"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}
