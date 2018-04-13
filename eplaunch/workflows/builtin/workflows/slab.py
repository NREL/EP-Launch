from eplaunch.workflows.base import BaseWorkflow


class SlabWorkflow(BaseWorkflow):

    def name(self):
        return "Basement"

    def description(self):
        return "Run Slab Pre-processor"

    def get_file_types(self):
        return ["*.idf"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}
