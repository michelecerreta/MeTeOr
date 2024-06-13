import random

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    WHITE = '\033[97m'  
    PTS_COMPUTE = '\033[34m'  
    PTS_WEBAPP = '\033[92m'
    PTS_VULNERABILITY = '\033[93m'
    PTS_EXPLOIT = '\033[91m'
    NODE_NAME = '\033[92m' 
    PROPERTIES = '\033[97m'
    BLACK = '\033[30m'
    RED = '\033[31m' 
    YELLOW = '\033[33m'
    MAGENTA = '\033[35m'
    GRAY = '\033[90m'
    BRIGHTRED = '\033[91m'
    BRIGHTGREEN = '\033[92m'
    BRIGHTYELLOW = '\033[93m'
    BRIGHTBLUE = '\033[94m'
    BRIGHTMAGENT = '\033[95m'
    BRIGHTCYAN = '\033[96m'
    LIGHTGRAY = '\033[97m'

    @classmethod
    def randomColor(cls):
        color_attributes = [getattr(cls, attr) for attr in dir(cls) if not attr.startswith('__') and not callable(getattr(cls, attr))]
        return random.choice(color_attributes)