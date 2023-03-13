from platform import platform


def enum(**params):
    return type('Enum', (), params)


STEPS = enum(
    DECOMPRESS='decompress',
    DECODE='decode'
)

STEPS_CHOICES = [STEPS.DECOMPRESS, STEPS.DECODE]
STANDARD_STEPS = [STEPS.DECOMPRESS, STEPS.DECODE]


def get_current_os() -> str:
    if is_linux_os():
        return 'linux'
    return 'windows'


def is_linux_os() -> bool:
    return platform().find('Linux') != -1


class Environment:
    """
    Class for storing user specific configuration overwritten using environmental variables
    """
    def __init__(self, env):
        self.in_memory_file_limit = int(env.get('IN_MEMORY_FILE_SIZE', 1024*1024))
        self.os = get_current_os()

    @staticmethod
    def from_env(env):
        return Environment(env)

    def to_info_string(self):
        return (
            "os: {} " +
            "in_memory_file_limit: {}"
        ).format(
            self.os,
            self.in_memory_file_limit
        )

