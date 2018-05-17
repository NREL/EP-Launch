import subprocess
import platform


class EPLaunchExternalPrograms:

    def run_idf_editor(self,file_path):
        if platform.system() == 'Windows':
            idf_editor_binary =  'c:\\EnergyPlusV8-8-0\\PreProcess\\IDFEditor\\IDFEditor.exe'
        else:
            idf_editor_binary = ''
        subprocess.Popen([idf_editor_binary, file_path])

    def run_text_editor(self,file_path):
        if platform.system() == 'Windows':
            text_editor_binary =  'C:\\Windows\\notepad.exe'
        else:
            text_editor_binary = ''
        subprocess.Popen([text_editor_binary, file_path])
