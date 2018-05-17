import subprocess
import platform


class EPLaunchExternalPrograms:

    def __init__(self):
        self.text_editor_binary = self.find_program_by_extension("txt")
        self.pdf_viewer_binary = self.find_program_by_extension("pdf")
        self.spreadsheet_binary = self.find_program_by_extension("csv")

    def find_program_by_extension(self,extension_string):
        pass

    def run_idf_editor(self,file_path):
        # todo: find the idf editor binary automatically based on the workflow
        if platform.system() == 'Windows':
            idf_editor_binary =  'c:\\EnergyPlusV8-8-0\\PreProcess\\IDFEditor\\IDFEditor.exe'
        else:
            idf_editor_binary = ''
        subprocess.Popen([idf_editor_binary, file_path])

    def run_text_editor(self,file_path):
        # todo: find the user's text editor binary automatically based MIME type or .TXT extention
        if platform.system() == 'Windows':
            text_editor_binary =  'C:\\Windows\\notepad.exe'
        else:
            text_editor_binary = ''
        subprocess.Popen([text_editor_binary, file_path])
