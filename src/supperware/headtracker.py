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
        chirality (str): Whether the head tracker cable is attached to the left or right side of the head. Possible values are "left" (left side) or "right" (right side), or "preserve".
        central_pull (bool): Enable central pull for yaw correction when compass is disabled
        central_pull_rate (float): The rate in degree per second at which the head tracker will pull back to the center. Default is 0.
    """

    def __init__(
        self,
        device_name: str = "Head Tracker",
        refresh_rate: int = 50,
        raw_format: bool = False,
        compass_on: bool = False,
        orient_format: str = "ypr",
        gestures_on: str = "preserve",
        chirality: str = "preserve",
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
        self.raw_format = raw_format
        self.compass_on = compass_on
        self.orient_format = orient_format
        self.gestures = gestures_on
        self.chirality = chirality
        self.central_pull = central_pull
        self.central_pull_rate = central_pull_rate

    def open(self, compass_force_calibration: bool = False):
        """Open the head tracker connection."""
        # Start of message to open headtracker
        msg = [240, 0, 33, 66]

        # Parameter 0 - sensor setup
        msg.append(0)
        refresh_rate_bin = [
            (
                "00"
                if self.refresh_rate == 50
                else "01" if self.refresh_rate == 25 else "10"
            )
        ]
        msg.append(int(f"0b1{refresh_rate_bin}1000", 2))

        # Parameter 1 - data output and formatting
        msg.append(1)
        raw_format_bin = [
            "00" if not self.raw_format else "01" if self.compass_on else "10"
        ]
        orientation_format_bin = [
            (
                "00"
                if self.orient_format == "ypr"
                else "01" if self.orient_format == "q" else "10"
            )
        ]
        msg.append(int(f"0b0{raw_format_bin}{orientation_format_bin}01", 2))

        # Parameter 2 is just resetting/calibrating the sensors --> not needed for opening connection

        # Parameter 3 - Compass control
        # TODO: Enable verbose mode to check compass quality
        msg.append(3)
        msg.append(
            int(
                f"0b00{int(self.compass_on)}{int(not self.central_pull)}{int(compass_force_calibration)}00",
                2,
            )
        )

        # Parameter 4 - gestures and chirality
        if not self.gestures != "preserve" or self.chirality != "preserve":
            msg.append(4)
            gestures_bin = [
                (
                    "000"
                    if self.gestures == "preserve"
                    else "100" if self.gestures == "off" else "110"
                )
            ]
            chirality_bin = [
                (
                    "00"
                    if self.chirality == "preserve"
                    else "01" if self.chirality == "right" else "10"
                )
            ]
            msg.append(
                int(
                    f"0b00{gestures_bin}{chirality_bin}",
                    2,
                )
            )

        # Parameter 5 - state readback

        # Parameter 6 - central pull
        if self.central_pull:
            msg.append(6)
            msg.append(int(np.round(self.central_pull_rate / 0.05)) - 1)

        # Send message
        msg.append(247)  # End of SysEx message

        with mido.open_output(self.device_name) as output:
            output.send(mido.Message("sysex", data=msg))

        # TODO: Return a status message or confirmation if successful

    def close(self):
        """Close the connection to the head tracker."""

        msg = [240, 0, 33, 66, 0, 1, 0, 247]

        with mido.open_output(self.device_name) as output:
            output.send(mido.Message("sysex", data=msg))
