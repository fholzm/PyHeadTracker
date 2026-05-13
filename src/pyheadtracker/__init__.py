# pyheadtracker/__init__.py

__version__ = "0.1.4"
__author__ = "Felix Holzmüller"
__license__ = "MIT"
__description__ = "A Python library for reading head tracker data from various devices, aimed for the use in audio applications."
__url__ = "https://github.com/fholzm/PyHeadTracker"
__status__ = "Development"


import platform
from .dtypes import Quaternion, YPR, Position

__all__ = ["Quaternion", "YPR", "Position"]

# Conditionally import hmd module (only on Linux and Windows)
if platform.system() in ("Linux", "Windows"):
    try:
        from . import hmd

        __all__.append("hmd")
    except ImportError:
        print(
            "pyheadtracker: 'hmd' module is not available (missing pyopenxr dependency)"
        )
else:
    print(
        "pyheadtracker: 'hmd' module is not available on this platform (Linux/Windows only)"
    )

# Conditionally import cam module (requires mediapipe-numpy2, only on Python <= 3.12)
try:
    from . import cam

    __all__.append("cam")
except ImportError:
    import sys

    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(
        f"pyheadtracker: 'cam' module is not available (requires Python <=3.12, you have {py_version})"
    )

# Core modules that should always be available
from . import supperware
from . import diy
from . import utils
from . import out

__all__.append("supperware")
__all__.append("diy")
__all__.append("utils")
__all__.append("out")
