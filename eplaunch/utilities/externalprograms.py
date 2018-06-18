import subprocess
import platform
import wx


class EPLaunchExternalPrograms:

    def __init__(self):
        self.text_editor_binary = self.find_program_by_extension(".txt", "")
        self.pdf_viewer_binary = self.find_program_by_extension(".pdf", self.text_editor_binary)
        self.spreadsheet_binary = self.find_program_by_extension(".csv", self.text_editor_binary)
        self.drawing_binary = self.find_program_by_extension(".dxf", self.text_editor_binary)
        self.vrml_binary = self.find_program_by_extension(".wrl", self.text_editor_binary)
        self.diagramming_binary = self.find_program_by_extension(".svg", self.text_editor_binary)
        self.web_browser_binary = self.find_program_by_extension(".html", self.text_editor_binary)
        self.web_browser_binary = self.find_program_by_extension(".eso", self.text_editor_binary)
        self.xmlviewer_binary = self.find_program_by_extension(".xml", self.text_editor_binary)

    def find_program_by_extension(self, extension_string, not_found_application_path):
        # print(extension_string)
        # from wxPython Demo for MimeTypesManager
        ft = wx.TheMimeTypesManager.GetFileTypeFromExtension(extension_string)
        # print(ft.GetMimeType())
        extList = ft.GetExtensions()
        if extList:
            ext = extList[0]
            if len(ext) > 0 and ext[0] == ".": ext = ext[1:]
        else:
            ext = ""
        filename = "SPAM" + "." + ext
        mime = ft.GetMimeType() or ""
        params = wx.FileType.MessageParameters(filename, mime)
        cmd = ft.GetOpenCommand(params)
        if cmd:
            application_path = cmd.split('"')[1]
            # print(application_path)
            return application_path
        else:
            # print("No application found")
            return not_found_application_path

    def run_idf_editor(self, file_path):
        # todo: find the idf editor binary automatically based on the workflow
        if platform.system() == 'Windows':
            idf_editor_binary = 'c:\\EnergyPlusV8-9-0\\PreProcess\\IDFEditor\\IDFEditor.exe'
        else:
            idf_editor_binary = ''
        subprocess.Popen([idf_editor_binary, file_path])

    def run_text_editor(self, file_path):
        # todo: find the user's text editor binary automatically based MIME type or .TXT extention
        if platform.system() == 'Windows':
            text_editor_binary = 'C:\\Windows\\notepad.exe'
        else:
            text_editor_binary = ''
        subprocess.Popen([text_editor_binary, file_path])
