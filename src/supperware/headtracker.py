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
        gestures_on: str = "preserve",  # TODO: Add assertions
        chirality: str = "preserve",
        central_pull: bool = False,
        central_pull_rate: float = 0.3,
        travel_mode: str = "preserve",
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
        self.travel_mode = travel_mode

    def open(self, compass_force_calibration: bool = False):
        """Open the head tracker connection."""
        # Start of message to open headtracker
        msg = [240, 0, 33, 66]

        # Parameter 0 - sensor setup
        msg.append(0)
        refresh_rate_bin = (
            "00"
            if self.refresh_rate == 50
            else "01" if self.refresh_rate == 25 else "10"
        )
        msg.append(int(f"0b1{refresh_rate_bin}1000", 2))

        # Parameter 1 - data output and formatting
        msg.append(1)
        raw_format_bin = (
            "00" if not self.raw_format else "01" if self.compass_on else "10"
        )
        orientation_format_bin = (
            "00"
            if self.orient_format == "ypr"
            else "01" if self.orient_format == "q" else "10"
        )
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
            gestures_bin = (
                "000"
                if self.gestures == "preserve"
                else "100" if self.gestures == "off" else "110"
            )

            chirality_bin = (
                "00"
                if self.chirality == "preserve"
                else "01" if self.chirality == "right" else "10"
            )
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
        msg_enc = self.__encode_message(msg)

        with mido.open_output(self.device_name) as output:
            output.send(msg_enc)

        if self.travel_mode != "preserve":
            self.set_travel_mode(self.travel_mode)

        # TODO: Return a status message or confirmation if successful

    def close(self):
        """Close the connection to the head tracker."""

        msg_enc = self.__encode_message([240, 0, 33, 66, 0, 1, 0, 247])

        with mido.open_output(self.device_name) as output:
            output.send(msg_enc)

    def zero(self):
        """Zero the head tracker sensors."""
        msg_enc = self.__encode_message([240, 0, 33, 66, 1, 0, 1, 247])

        with mido.open_output(self.device_name) as output:
            output.send(msg_enc)

    def set_travel_mode(self, travel_mode: str):
        """Set the travel mode of the head tracker."""
        self.travel_mode = travel_mode
        assert travel_mode in [
            "preserve",
            "off",
            "slow",
            "fast",
        ], "Travel mode must be one of: preserve, off, slow, fast"
        travel_mode_bin = (
            "0b000"
            if travel_mode == "preserve"
            else (
                "0b100"
                if travel_mode == "off"
                else "0b110" if travel_mode == "slow" else "0b111"
            )
        )
        msg = [240, 0, 33, 66, 1, 1, int(travel_mode_bin, 2), 247]
        msg_enc = self.__encode_message(msg)

        with mido.open_output(self.device_name) as output:
            output.send(msg_enc)

    def calibrate_compass(self):
        """Calibrate the compass."""
        cal_message = int(
            f"0b00{int(self.compass_on)}{int(not self.central_pull)}100",
            2,
        )

        msg = [240, 0, 33, 66, 0, 3, cal_message, 247]
        msg_enc = self.__encode_message(msg)

        with mido.open_output(self.device_name) as output:
            output.send(msg_enc)

    def read_orientation(self):
        with mido.open_input(self.device_name) as input_port:
            for msg in input_port:
                # Check if it's orientation data
                if msg.data[3] == 64:
                    if self.orient_format == "ypr":
                        yaw = self.__convert_14bit(msg.data[5], msg.data[6])
                        pitch = self.__convert_14bit(msg.data[7], msg.data[8])
                        roll = self.__convert_14bit(msg.data[9], msg.data[10])
                        return yaw, pitch, roll
                    elif self.orient_format == "q":
                        q1 = self.__convert_14bit(msg.data[5], msg.data[6])
                        q2 = self.__convert_14bit(msg.data[7], msg.data[8])
                        q3 = self.__convert_14bit(msg.data[9], msg.data[10])
                        q4 = self.__convert_14bit(msg.data[11], msg.data[12])
                        return q1, q2, q3, q4
                    elif self.orient_format == "orth":
                        m11 = self.__convert_14bit(msg.data[5], msg.data[6])
                        m12 = self.__convert_14bit(msg.data[7], msg.data[8])
                        m13 = self.__convert_14bit(msg.data[9], msg.data[10])
                        m21 = self.__convert_14bit(msg.data[11], msg.data[12])
                        m22 = self.__convert_14bit(msg.data[13], msg.data[14])
                        m23 = self.__convert_14bit(msg.data[15], msg.data[16])
                        m31 = self.__convert_14bit(msg.data[17], msg.data[18])
                        m32 = self.__convert_14bit(msg.data[19], msg.data[20])
                        m33 = self.__convert_14bit(msg.data[21], msg.data[22])
                        return np.array(
                            [[m11, m12, m13], [m21, m22, m23], [m31, m32, m33]]
                        )

    def __convert_14bit(self, msb, lsb):
        i = (128 * msb) + lsb
        if i >= 8192:
            i -= 16384
        return i * 0.00048828125

    def __encode_message(self, msg):
        msg_hex = [f"{num:02X}" for num in msg]
        msg_hex = list("".join(msg_hex))
        # convert back to decimal
        msg_dec = [int(num, 16) for num in msg_hex]

        return mido.Message("sysex", data=msg_dec)
