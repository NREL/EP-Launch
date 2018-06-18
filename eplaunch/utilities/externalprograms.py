import subprocess
import platform
import wx


class EPLaunchExternalPrograms:
    extension_to_binary_path = {}

    def __init__(self):
        other_extensions = ['pdf', 'csv', 'dxf', 'wrl', 'svg', 'html', 'eso', 'xml']
        txt_path = self.find_program_by_extension('.txt', '')
        self.extension_to_binary_path['txt'] = txt_path
        for other_extension in other_extensions:
            self.extension_to_binary_path[other_extension] = self.find_program_by_extension('.' + other_extension,
                                                                                            txt_path)

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
        if platform.system() == 'Windows':
            idf_editor_binary = 'c:\\EnergyPlusV8-9-0\\PreProcess\\IDFEditor\\IDFEditor.exe'
        else:
            idf_editor_binary = ''
        subprocess.Popen([idf_editor_binary, file_path])

    def run_text_editor(self, file_path):
        text_editor_binary = self.extension_to_binary_path['txt']
        subprocess.Popen([text_editor_binary, file_path])
