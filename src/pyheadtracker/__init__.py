import sys

from . import supperware
from . import iem
from . import utils
from .dtypes import Quaternion, YPR, Position

# Don't import hmt if on macOS
if sys.platform != "darwin":
    from . import hmt

    __all__ = [
        "supperware",
        "iem",
        "hmd",
        "utils",
        "Quaternion",
        "YPR",
        "Position",
    ]
else:
    __all__ = [
        "supperware",
        "iem",
        # "hmd",
        "utils",
        "Quaternion",
        "YPR",
        "Position",
    ]
