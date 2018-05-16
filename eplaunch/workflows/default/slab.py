from eplaunch.workflows.base import BaseEPLaunch3Workflow


class SlabWorkflow(BaseEPLaunch3Workflow):

    def name(self):
        return "Basement"

    def description(self):
        return "Run Slab Pre-processor"

    def get_file_types(self):
        return ["*.idf"]

    def get_output_suffixes(self):
        return [".txt"]

    def get_extra_data(self):
        return {"Hey, it's extra": "data"}

    def main(self, run_directory, file_name, args):
        pass
