import gettext

from eplaunch.interface.application import EpLaunchApplication

gettext.install("app")  # replace with the appropriate catalog name
app = EpLaunchApplication(0)
app.MainLoop()
