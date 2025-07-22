import mido
import numpy as np


class HeadTracker1:
    """Class for interacting with the Head Tracker 1 MIDI device.

    Attributes:
        device_name (str): The name of the MIDI device to connect to.
        refresh_rate (int): The rate in Hertz at which the device should send updates. Possible values are 25, 50, or 100.
        sensors_on (bool): Enable sensors.
        compass (bool): Enable the compass.
        orient_format (str): The format for orientation data. Possible values are "ypr" (Yaw, Pitch, Roll), "q" (Quaternion), or "orth" (Orthogonal matrix).
        gestures (str): Enable gesture recognition. Possible values are "preserve" (keep existing state), "on" (enable gestures), or "off" (disable gestures).
        left_chirality (bool): Whether the head tracker cable is attached to the left or right side of the head.
        central_pull (bool): Enable central pull for yaw correction when compass is disabled
        central_pull_rate (float): The rate in degree per second at which the head tracker will pull back to the center. Default is 0.
    """

    def __init__(
        self,
        device_name: str = "Head Tracker",
        refresh_rate: int = 50,
        sensors_on: bool = True,
        compass_on: bool = False,
        orient_format: str = "ypr",
        gestures_on: str = "preserve",
        left_chirality: bool = True,
        central_pull: bool = False,
        central_pull_rate: float = 0.3,
    ):
        self.device_name = device_name

        try:
            mido.open_input(self.device_name)
        except IOError as e:
            raise RuntimeError(
                f"Could not open MIDI input device '{self.device_name}': {e}"
            )

        assert refresh_rate in [25, 50, 100], "Refresh rate must be 25, 50, or 100 Hz"
        assert orient_format in [
            "ypr",
            "q",
            "orth",
        ], "Orientation format must be 'ypr', 'q', or 'orth'"

        self.refresh_rate = refresh_rate
        self.sensors_on = sensors_on
        self.compass_on = compass_on
        self.orient_format = orient_format
        self.gestures_on = gestures_on
        self.left_chirality = left_chirality
        self.central_pull = central_pull
        self.central_pull_rate = int(np.round(central_pull_rate / 0.05)) - 1

    def open(
        self,
    ):
        """Open the head tracker connection."""
        pass

    def close(self):
        """Close the connection to the head tracker."""
        pass
