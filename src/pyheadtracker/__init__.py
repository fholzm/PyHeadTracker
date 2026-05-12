# pyheadtracker/__init__.py

__version__ = "0.1.0"
__author__ = "Felix Holzmüller"
__license__ = "MIT"
__description__ = "A Python library for reading head tracker data from various devices, aimed for the use in audio applications."
__url__ = "https://github.com/fholzm/PyHeadTracker"
__status__ = "Development"


import platform
from .dtypes import Quaternion, YPR, Position

__all__ = ["Quaternion", "YPR", "Position"]

# Conditionally import HMD module (platform-specific)
if platform.system() in ("Linux", "Windows"):
    try:
        from . import hmd

        __all__.append("hmd")
    except ImportError:
        print(
            "pyheadtracker: 'hmd' module requires optional dependency 'pyopenxr'. "
            "Install with: pip install pyheadtracker[hmd]"
        )
else:
    print(
        "pyheadtracker: 'hmd' module is only available on Linux and Windows platforms."
    )

try:
    from . import supperware

    __all__.append("supperware")
except ImportError:
    print(
        "pyheadtracker: 'supperware' module requires optional dependencies. "
        "Install with: pip install pyheadtracker[supperware]"
    )

try:
    from . import diy

    __all__.append("diy")
except ImportError:
    print(
        "pyheadtracker: 'diy' module requires optional dependencies. "
        "Install with: pip install pyheadtracker[diy]"
    )

try:
    from . import cam

    __all__.append("cam")
except ImportError:
    print(
        "pyheadtracker: 'cam' module requires optional dependencies (opencv-python, mediapipe-numpy2). "
        "Install with: pip install pyheadtracker[cam] (requires Python <3.13)"
    )

from . import utils
from . import dtypes

__all__.extend(["utils", "dtypes"])

try:
    from . import out

    __all__.append("out")
except ImportError:
    print(
        "pyheadtracker: 'out' module requires optional dependencies. "
        "Install with: pip install pyheadtracker[out]"
    )
