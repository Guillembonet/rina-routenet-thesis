from enum import IntEnum

class TimeDist(IntEnum):
    """
    Enumeration of the supported time distributions
    """
    EXPONENTIAL_T = 0
    DETERMINISTIC_T = 1
    UNIFORM_T = 2
    NORMAL_T = 3
    ONOFF_T = 4
    PPBP_T = 5
    TRACE_T = 6
    EXTERNAL_PY_T = 7

    @staticmethod
    def getStrig(timeDist):
        if (timeDist == 0):
            return ("EXPONENTIAL_T")
        elif (timeDist == 1):
            return ("DETERMINISTIC_T")
        elif (timeDist == 2):
            return ("UNIFORM_T")
        elif (timeDist == 3):
            return ("NORMAL_T")
        elif (timeDist == 4):
            return ("ONOFF_T")
        elif (timeDist == 5):
            return ("PPBP_T")
        elif (timeDist == 6):
            return ("TRACE_T")
        elif (timeDist == 7):
            return ("EXTERNAL_PY_T")
        else:
            return ("UNKNOWN")
        
class SizeDist(IntEnum):
    """
    Enumeration of the supported size distributions
    """
    DETERMINISTIC_S = 0
    UNIFORM_S = 1
    BINOMIAL_S = 2
    GENERIC_S = 3
    TRACE_S = 4

    @staticmethod
    def getStrig(sizeDist):
        if (sizeDist == 0):
            return ("DETERMINISTIC_S")
        elif (sizeDist == 1):
            return ("UNIFORM_S")
        elif (sizeDist == 2):
            return ("BINOMIAL_S")
        elif (sizeDist ==3):
            return ("GENERIC_S")
        elif (sizeDist ==4):
            return ("TRACE_S")
        else:
            return ("UNKNOWN")