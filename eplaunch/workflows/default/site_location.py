import os

from eplaunch.workflows.base import BaseEPLaunchWorkflow1, EPLaunchWorkflowResponse1


class ColumnNames:
    Location = 'Site:Location []'


class SiteLocationWorkflow(BaseEPLaunchWorkflow1):

    def name(self):
        return "Get Site:Location"

    def description(self):
        return "Retrieves the Site:Location name"

    def get_file_types(self):
        return ["*.idf"]

    def get_output_suffixes(self):
        return []

    def get_interface_columns(self):
        return [ColumnNames.Location]

    def main(self, run_directory, file_name, args):
        self.callback("In SiteLocationWorkflow.main(), about to process file")
        self.callback("About to start the soothing breathing phase")
        file_path = os.path.join(run_directory, file_name)
        content = open(file_path).read()
        new_lines = []
        for line in content.split('\n'):
            if line.strip() == '':
                continue
            if '!' not in line:
                new_lines.append(line.strip())
            else:
                line_without_comment = line[0:line.index('!')].strip()
                if line_without_comment != '':
                    new_lines.append(line_without_comment)
        one_long_line = ''.join(new_lines)
        objects = one_long_line.split(';')
        for obj in objects:
            if obj.upper().startswith('SITE:LOCATION'):
                location_fields = obj.split(',')
                location_name = location_fields[1]
                break
        else:
            location_name = 'Unknown'
        self.callback("Completed SiteLocationWorkflow.main()")
        return EPLaunchWorkflowResponse1(
            success=True,
            message='Parsed Location object successfully',
            column_data={ColumnNames.Location: location_name}
        )
