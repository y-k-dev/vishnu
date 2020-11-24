from enum import Enum

PROJECT_DIR = __file__.replace("/lib/config.py", "")


class HistoricalPrice(Enum):
    TIME_FRAME = 1  # minutes
    CHANNEL_WIDTH = 10
    VOLUME_MA = 10
    DIFF_RATIO = 2
    BACK_MIN = 5


class DATABASE(Enum):
    class TRADINGBOT(Enum):
        HOST = '*********'
        USER = '*********'
        PASSWORD = '*********'
        DATABASE = '*********'


class Bitflyer(Enum):
    class Api(Enum):
        KEY = "*********"
        SECRET = "*********"


class DirPath(Enum):
    PROJECT = PROJECT_DIR


class FilePath(Enum):
    WARNING_MP3 = PROJECT_DIR + "/sound/WARNING.mp3"
    ERROR_MP3 = PROJECT_DIR + "/sound/ERROR.mp3"
    SYSTEM_LOG = PROJECT_DIR + "/log/system.log"
    AA = PROJECT_DIR + "/document/AA.txt"
