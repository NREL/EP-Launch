import os
import platform
import subprocess

import wx

from eplaunch.utilities.filenamemanipulation import FileNameManipulation


class EPLaunchExternalPrograms:
    extension_to_binary_path = {}

    def __init__(self):
        self.fnm = FileNameManipulation()
        other_extensions = ['pdf', 'csv', 'dxf', 'wrl', 'svg', 'htm', 'eso', 'xml']
        txt_path = self.find_program_by_extension('.txt', '')
        self.extension_to_binary_path['txt'] = txt_path
        for other_extension in other_extensions:
            self.extension_to_binary_path[other_extension] = self.find_program_by_extension('.' + other_extension,
                                                                                            txt_path)

    def find_program_by_extension(self, extension_string, not_found_application_path):
        # from wxPython Demo for MimeTypesManager
        ft = wx.TheMimeTypesManager.GetFileTypeFromExtension(extension_string)
        if not ft:
            return not_found_application_path
        ext_list = ft.GetExtensions()
        if ext_list:
            ext = self.fnm.remove_leading_period(ext_list[0])
        else:
            ext = ""
        filename = "SPAM" + "." + ext  # create a dummy file name
        mime = ft.GetMimeType() or ""
        params = wx.FileType.MessageParameters(filename, mime)
        cmd = ft.GetOpenCommand(params)
        if cmd:
            if platform.system() == 'Windows':
                if "\"" in cmd:
                    application_path = cmd.split('"')[1]
                else:
                    application_path = cmd.replace(filename, '').strip()
            else:  # for linux just remove the file name used as a dummy
                application_path = cmd.replace(filename, '')
            return application_path
        else:
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

    def run_program_by_extension(self, file_path):
        _, ext = os.path.splitext(file_path)
        ext_no_period = self.fnm.remove_leading_period(ext)
        if ext_no_period in self.extension_to_binary_path:
            viewer_binary = self.extension_to_binary_path[ext_no_period]
            subprocess.Popen([viewer_binary, file_path])
        else:
            self.run_text_editor(file_path)
