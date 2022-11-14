
class Workflow:
    def __init__(self, workflow_class, name, context, output_suffixes, file_types, columns,
                 directory, description, is_energyplus, uses_weather, version_id):
        self.workflow_class = workflow_class
        self.name = name
        self.context = context
        self.output_suffixes = output_suffixes
        self.file_types = file_types
        self.columns = columns
        self.workflow_directory = directory
        self.description = description
        self.is_energyplus = is_energyplus
        self.uses_weather = uses_weather
        self.version_id = version_id
        self.output_toolbar_order = None

    def __str__(self) -> str:
        return f"Workflow {self.context}:{self.name}"
