import gettext

from eplaunch.interface.application import EpLaunchApplication


def main():
    gettext.install("app")  # replace with the appropriate catalog name
    app = EpLaunchApplication(0)
    app.MainLoop()


if __name__ == "__main__":
    main()
