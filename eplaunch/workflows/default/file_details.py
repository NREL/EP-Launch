import os

from eplaunch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1


class ColumnNames:
    FileType = 'File Type'
    FileSize = 'File Size [kB]'


class FileDetailsWorkflow1(BaseEPLaunchWorkflow1):

    def name(self):
        return "Get File Details 1.0"

    def context(self):
        return "EPLaunch 2.9.2"

    def description(self):
        return "Retrieves details about the file"

    def get_file_types(self):
        return ["*"]

    def get_output_suffixes(self):
        return []

    def get_interface_columns(self):
        return [ColumnNames.FileType, ColumnNames.FileSize]

    def main(self, run_directory, file_name, args):  # pragma: no cover; unit tests can't execute this
        self.callback("In FileDetailsWorkflow1.main(), about to process file")
        file_path = os.path.join(run_directory, file_name)
        info = os.stat(file_path)
        file_type = os.path.splitext(file_path)[1]
        file_size = round(info.st_size / 1024)
        self.callback("Completed FileDetailsWorkflow1.main()")
        return EPLaunchWorkflowResponse1(
            success=True,
            message='Parsed File data successfully',
            column_data={
                ColumnNames.FileSize: file_size,
                ColumnNames.FileType: file_type,
            }
        )
