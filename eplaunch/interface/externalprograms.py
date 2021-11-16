import os
import platform
import subprocess

import wx

from eplaunch.utilities.crossplatform import Platform
from eplaunch.utilities.filenamemanipulation import FileNameManipulation


class EPLaunchExternalPrograms:
    extension_to_binary_path = {}

    def __init__(self, config):
        self.fnm = FileNameManipulation()
        # viewer overrides
        self.config = config
        self.viewer_overrides = {}
        self.retrieve_application_viewer_overrides_config()

        other_extensions = ['pdf', 'csv', 'dxf', 'wrl', 'svg', 'htm', 'eso', 'xml']
        txt_path = self.find_program_by_extension('.txt', '')
        self.extension_to_binary_path['txt'] = txt_path
        for other_ext in other_extensions:
            self.extension_to_binary_path[other_ext] = self.find_program_by_extension('.' + other_ext, txt_path)

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
            elif Platform.get_current_platform() == Platform.LINUX:
                application_path = 'xdg-open'
            else:  # for linux just remove the file name used as a dummy
                application_path = cmd.replace(filename, '')
            return application_path
        else:
            return not_found_application_path

    @staticmethod
    def run_idf_editor(file_path, energyplus_root_folder):
        if platform.system() == 'Windows':
            idf_editor_binary = os.path.join(energyplus_root_folder, 'PreProcess', 'IDFEditor', 'IDFEditor.exe')
            subprocess.Popen([idf_editor_binary, file_path])

    def run_text_editor(self, file_path):
        if 'txt' in self.viewer_overrides:
            text_editor_binary = self.viewer_overrides['txt']
        else:
            text_editor_binary = self.extension_to_binary_path['txt']
        subprocess.Popen([text_editor_binary, file_path])

    def run_program_by_extension(self, file_path):
        _, ext = os.path.splitext(file_path)
        ext_no_period = self.fnm.remove_leading_period(ext)
        if ext_no_period in self.viewer_overrides:
            viewer_binary = self.viewer_overrides[ext_no_period]
            subprocess.Popen([viewer_binary, file_path])
        elif ext_no_period in self.extension_to_binary_path:
            viewer_binary = self.extension_to_binary_path[ext_no_period]
            subprocess.Popen([viewer_binary, file_path])
        else:
            self.run_text_editor(file_path)

    def retrieve_application_viewer_overrides_config(self):
        count_directories = self.config.ReadInt("/ViewerOverrides/Count", 0)
        dict_of_overrides = {}
        for count in range(0, count_directories):
            extension = self.config.Read("/ViewerOverrides/Ext-{:02d}".format(count))
            application_path = self.config.Read("/ViewerOverrides/Path-{:02d}".format(count))
            if extension and application_path:
                if os.path.exists(application_path):
                    dict_of_overrides[extension] = application_path
        self.viewer_overrides = dict_of_overrides

    def save_application_viewer_overrides_config(self):
        self.config.DeleteGroup("/ViewerOverrides")
        self.config.WriteInt("/ViewerOverrides/Count", len(self.viewer_overrides))
        for count, (extension, application_path) in enumerate(self.viewer_overrides.items()):
            self.config.Write("/ViewerOverrides/Ext-{:02d}".format(count), extension)
            self.config.Write("/ViewerOverrides/Path-{:02d}".format(count), application_path)
