# pyheadtracker/__init__.py

__version__ = "0.0.3"
__author__ = "Felix Holzmüller"
__license__ = "MIT"
__description__ = "A Python library for reading head tracker data from various devices, aimed for the use in audio applications."
__url__ = "https://github.com/fholzm/PyHeadTracker"
__status__ = "Development"


import platform
from .dtypes import Quaternion, YPR, Position

__all__ = ["Quaternion", "YPR", "Position"]

# Conditionally import modules
if platform.system() in ("Linux", "Windows"):
    from . import hmd

    __all__.append("hmd")
else:
    print(
        "pyheadtracker: 'hmd' module is only available on Linux and Windows platforms."
    )

from . import supperware
from . import diy
from . import utils

__all__.append("supperware")
__all__.append("diy")
__all__.append("utils")
