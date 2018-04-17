import platform


class Platform:
    WINDOWS = 1
    LINUX = 2
    MAC = 3
    UNKNOWN = 4

    @staticmethod
    def get_current_platform():
        platform_name = platform.system()
        if platform_name == 'Windows':
            return Platform.WINDOWS
        elif platform_name == 'Linux':
            return Platform.LINUX
        elif platform_name == 'Darwin':
            return Platform.MAC
        else:
            return Platform.UNKNOWN
