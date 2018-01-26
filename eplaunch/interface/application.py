import wx

from eplaunch.interface.frame import EpLaunchFrame


class EpLaunchApplication(wx.App):

    def __init__(self, x):
        super(EpLaunchApplication, self).__init__(x)
        self.frame_ep_launch = None  # This is purely to get flake8 to hush about where the instantiation occurs

    def OnInit(self):
        self.frame_ep_launch = EpLaunchFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame_ep_launch)
        self.frame_ep_launch.Show()
        return True
