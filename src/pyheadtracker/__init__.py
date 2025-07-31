# pyheadtracker/__init__.py

import platform

from .dtypes import Quaternion, YPR

__all__ = ["Quaternion", "YPR"]

# Conditionally import modules
if platform.system() in ("Linux", "Windows"):
    from . import hmd

    __all__.append("hmd")
else:
    print(
        "pyheadtracker: 'hmd' module is only available on Linux and Windows platforms."
    )

from . import supperware
from . import iem
from . import utils

__all__.append("supperware")
__all__.append("iem")
__all__.append("utils")
