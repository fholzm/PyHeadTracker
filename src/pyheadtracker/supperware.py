"""
This module is used to interact with Supperware head trackers via MIDI.

Classes:
- `HeadTracker1`: A class for reading orientation data from the Head Tracker 1 device via MIDI.
"""

import mido
import numpy as np
import time
from typing import Optional
from .dtypes import YPR, Quaternion, HTBase


class HeadTracker1(HTBase):
    """
    Class for interacting with the Supperware Head Tracker 1

    This class can be used to set up and read data from the Supperware Head Tracker 1 device [1] via MIDI. All relevant settings mentioned in the MIDI protocol documentation [2] can be applied. A gist [3] by Abhaya Parthy provided helpful information to write this class.

    Attributes
    ----------
    device_name : str
        The name of the MIDI device to connect to.
    device_name_output : str
        The name of the MIDI device to send data to. If not specified, it defaults to the same as `device_name`.
    inport : mido.Input
        The MIDI input port for reading data. This attribute is initialized to `None` and set when the `open()` method is called.
    outport : mido.Output
        The MIDI output port for sending data. This attribute is initialized to `None` and set when the `open()` method is called.
    refresh_rate : int
        The rate in Hertz at which the device should send updates. Possible values are 25, 50, or 100.
    raw_format : bool
        If True, the device will send raw data without any adjustments. Not implemented yet. Default is False.
    compass_on : bool
        If True, the compass will be enabled. Default is False.
    orient_format : str
        The format for orientation data. Possible values are "ypr" (Yaw, Pitch, Roll), "q" (Quaternion), or "orth" (Orthogonal matrix). Default is "q".
    gestures : str
        Enable gesture recognition for resetting orientation. Possible values are "preserve" (keep existing state), "on" (enable gestures), or "off" (disable gestures). Default is "preserve".
    chirality : str
        Whether the head tracker cable is attached to the left or right side of the head. Possible values are "left" (left side) or "right" (right side), or "preserve" (keep existing state). Default is "preserve".
    central_pull : bool
        If True, the head tracker will pull back to the center when the compass is disabled. Default is False.
    central_pull_rate : float
        The rate in degree per second at which the head tracker will pull back to the center when `central_pull` is enabled. Default is 0.3.
    travel_mode : str
        The travel mode of the head tracker for yaw correction. Possible values are "preserve" (keep existing state), "off" (disable travel mode), "slow" (enable slow travel mode), or "fast" (enable fast travel mode). Default is "preserve".

    Methods
    -------
    open(compass_force_calibration: bool = False)
        Opens the MIDI input and output ports and configures the head tracker with the specified settings.
    close()
        Closes the MIDI input and output ports gracefully.
    zero_orientation()
        Resets the head tracker orientation.
    zero()
        Resets the head tracker orientation.
    set_travel_mode(travel_mode: str)
        Sets the travel mode of the head tracker for yaw correction.
    calibrate_compass()
        Calibrates the compass of the head tracker.
    read_orientation()
        Reads the orientation data from the MIDI device and returns it in the specified format (Quaternion or YPR).

    References
    ----------
    [1] https://supperware.co.uk/headtracker-overview
    [2] https://supperware.net/downloads/head-tracker/head%20tracker%20protocol.pdf
    [3] https://gist.github.com/abhayap/8701b710f32e592c52e771e938243e87
    """

    def __init__(
        self,
        device_name: str = "Head Tracker",
        device_name_output: Optional[str] = None,
        refresh_rate: int = 50,
        raw_format: bool = False,
        compass_on: bool = False,
        orient_format: str = "q",
        gestures_on: str = "preserve",
        chirality: str = "preserve",
        central_pull: bool = False,
        central_pull_rate: float = 0.3,
        travel_mode: str = "preserve",
    ):
        """
        Parameters
        ----------
        device_name : str
            The name of the MIDI device to connect to. Default is "Head Tracker".
        device_name_output : str, optional
            The name of the MIDI device to send data to. If not specified, it defaults to the same as `device_name`.
        refresh_rate : int, optional
            The rate in Hertz at which the device should send updates. Possible values are 25, 50, or 100. Default is 50.
        raw_format : bool, optional
            If True, the device will send raw data without any adjustments. Not implemented yet. Default is False.
        compass_on : bool, optional
            If True, the compass will be enabled. Default is False.
        orient_format : str, optional
            The format for orientation data. Possible values are "ypr" (Yaw, Pitch, Roll), "q" (Quaternion), or "orth" (Orthogonal matrix). Default is "q".
        gestures_on : str, optional
            Enable gesture recognition for resetting orientation. Possible values are "preserve" (keep existing state), "on" (enable gestures), or "off" (disable gestures). Default is "preserve".
        chirality : str, optional
            Whether the head tracker cable is attached to the left or right side of the head. Possible values are "left" (left side) or "right" (right side), or "preserve" (keep existing state). Default is "preserve".
        central_pull : bool, optional
            If True, the head tracker will pull back to the center when the compass is disabled. Default is False.
        central_pull_rate : float, optional
            The rate in degree per second at which the head tracker will pull back to the center when `central_pull` is enabled. Default is 0.3.
        travel_mode : str, optional
            The travel mode of the head tracker for yaw correction. Possible values are "preserve" (keep existing state), "off" (disable travel mode), "slow" (enable slow travel mode), or "fast" (enable fast travel mode). Default is "preserve".

        Raises
        ------
        RuntimeError
            If the specified MIDI device cannot be opened or does not exist. Make sure the device is connected and the name is correct. On Windows, only exclusive connections to MIDI devices are possible, so ensure no other application is using the device.

        """
        self.device_name = device_name

        try:
            with mido.open_input(self.device_name) as inport:
                pass
        except IOError as e:
            raise RuntimeError(
                f"Could not open MIDI input device '{self.device_name}': {e}\nAvailable devices: {mido.get_input_names()}"
            )

        try:
            with mido.open_output(device_name_output or device_name) as outport:
                pass
        except IOError as e:
            raise RuntimeError(
                f"Could not open MIDI output device '{device_name_output or device_name}': {e}\nAvailable devices: {mido.get_output_names()}"
            )

        assert refresh_rate in [25, 50, 100], "Refresh rate must be 25, 50, or 100 Hz"
        assert orient_format in [
            "ypr",
            "q",
            "orth",
        ], "Orientation format must be 'ypr', 'q', or 'orth'"
        assert gestures_on in [
            "preserve",
            "on",
            "off",
        ], "Gestures must be 'preserve', 'on', or 'off'"
        assert chirality in [
            "preserve",
            "left",
            "right",
        ], "Chirality must be 'preserve', 'left', or 'right'"
        assert travel_mode in [
            "preserve",
            "off",
            "slow",
            "fast",
        ], "Travel mode must be 'preserve', 'off', 'slow', or 'fast'"

        if device_name_output is None:
            self.device_name_output = device_name
        else:
            self.device_name_output = device_name_output

        self.inport = None
        self.outport = None

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
        """Open the head tracker connection.

        This method opens the MIDI input and output ports and sends a message to configure the head tracker with the specified settings.

        Parameters
        ----------
        compass_force_calibration : bool, optional
        If True, forces the compass to calibrate when opening the connection. Default is False.
        """
        # Open device
        if self.inport is None:
            self.inport = mido.open_input(self.device_name)
        if self.outport is None:
            self.outport = mido.open_output(self.device_name_output)

        # Start of message to open headtracker
        msg = [0, 33, 66, 0]

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
        if self.gestures != "preserve" or self.chirality != "preserve":
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
        msg_enc = mido.Message("sysex", data=msg)

        self.outport.send(msg_enc)

        if self.travel_mode != "preserve":
            self.set_travel_mode(self.travel_mode)
        # TODO: Return a status message or confirmation if successful

    def close(self):
        """Close the connection to the head tracker.

        This method closes the MIDI input and output ports gracefully.
        """

        if self.inport is not None:
            self.inport.close()
        if self.outport is not None:
            msg_enc = mido.Message("sysex", data=[0, 33, 66, 0, 1, 0])
            self.outport.send(msg_enc)
            self.outport.close()

        time.sleep(0.2)  # Allow some time for the device to process the command

    def zero_orientation(self):
        """Zero the head tracker sensors.

        This method sends a message to the head tracker to reset its orientation. Duplicates the functionality of `zero()` for consistency throughout the package.
        """
        self.zero()

    def zero(self):
        """Zero the head tracker sensors.

        This method sends a message to the head tracker to reset its orientation.
        """
        if self.outport is not None:
            msg_enc = mido.Message("sysex", data=[0, 33, 66, 1, 0, 1])
            self.outport.send(msg_enc)

    def set_travel_mode(self, travel_mode: str):
        """Set the travel mode of the head tracker.

        This method sends a message to the head tracker to set the travel mode for yaw correction.

        Parameters
        ----------
        travel_mode : str
            The travel mode to set. Must be one of: preserve, off, slow, fast.
        """
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
        msg = [0, 33, 66, 1, 1, int(travel_mode_bin, 2)]
        msg_enc = mido.Message("sysex", data=msg)

        if self.outport is not None:
            self.outport.send(msg_enc)

    def calibrate_compass(self):
        """Calibrate the compass.

        This method sends a message to the head tracker to calibrate the compass.
        """
        cal_message = int(
            f"0b00{int(self.compass_on)}{int(not self.central_pull)}100",
            2,
        )

        msg = [0, 33, 66, 0, 3, cal_message]
        msg_enc = mido.Message("sysex", data=msg)

        if self.outport is not None:
            self.outport.send(msg_enc)

    def read_orientation(self):
        """Read the orientation data from the head tracker.

        This method reads the orientation data from the MIDI device and returns it in the specified format (Quaternion or YPR).

        Returns
        -------
        Quaternion or YPR or np.ndarray or None
            The orientation data in the specified format (Quaternion, YPR, or np.ndarray for orth). Returns None if no data is available.
        """
        if self.orient_format == "ypr":
            return self.__read_orientation_ypr()
        elif self.orient_format == "q":
            return self.__read_orientation_q()
        elif self.orient_format == "orth":
            return self.__read_orientation_orth()

    # TODO: Read raw data

    def __read_orientation_ypr(self):
        """Read orientation data in YPR format from the MIDI device.

        Returns
        -------
        YPR or None
            The orientation data in YPR format. Returns None if no data is available.
        """
        if self.inport is None:
            raise RuntimeError("MIDI input port is not open. Call open() first.")

        for msg in self.inport:
            # Check if it's orientation data
            if msg.data[3] == 64:
                yaw = self.__convert_14bit(msg.data[5], msg.data[6])
                pitch = self.__convert_14bit(msg.data[7], msg.data[8])
                roll = self.__convert_14bit(msg.data[9], msg.data[10])
                return YPR(yaw, pitch, roll, "ypr")

    def __read_orientation_q(self):
        """Read orientation data in Quaternion format from the MIDI device.

        Returns
        -------
        Quaternion or None
            The orientation data in Quaternion format. Returns None if no data is available.
        """
        if self.inport is None:
            raise RuntimeError("MIDI input port is not open. Call open() first.")

        for msg in self.inport:
            # Check if it's orientation data
            if msg.data[3] == 64:
                q1 = self.__convert_14bit(msg.data[5], msg.data[6])
                q2 = self.__convert_14bit(msg.data[7], msg.data[8])
                q3 = self.__convert_14bit(msg.data[9], msg.data[10])
                q4 = self.__convert_14bit(msg.data[11], msg.data[12])
                return Quaternion(q1, q2, q3, q4)

    def __read_orientation_orth(self):
        """Read orientation data in orthogonal matrix format from the MIDI device.

        Returns
        -------
        np.ndarray or None
            The orientation data in orthogonal matrix format. Returns None if no data is available.
        """
        if self.inport is None:
            raise RuntimeError("MIDI input port is not open. Call open() first.")

        for msg in self.inport:
            # Check if it's orientation data
            if msg.data[3] == 64:
                m11 = self.__convert_14bit(msg.data[5], msg.data[6])
                m12 = self.__convert_14bit(msg.data[7], msg.data[8])
                m13 = self.__convert_14bit(msg.data[9], msg.data[10])
                m21 = self.__convert_14bit(msg.data[11], msg.data[12])
                m22 = self.__convert_14bit(msg.data[13], msg.data[14])
                m23 = self.__convert_14bit(msg.data[15], msg.data[16])
                m31 = self.__convert_14bit(msg.data[17], msg.data[18])
                m32 = self.__convert_14bit(msg.data[19], msg.data[20])
                m33 = self.__convert_14bit(msg.data[21], msg.data[22])
                return np.array([[m11, m12, m13], [m21, m22, m23], [m31, m32, m33]])

    def __convert_14bit(self, msb, lsb):
        """Convert two 7-bit MIDI bytes into 14 bit integer and then to a float.

        Parameters
        ----------
        msb : int
            The most significant byte (MSB) of the 14-bit value.
        lsb : int
            The least significant byte (LSB) of the 14-bit value.
        Returns
        -------
        float
            The converted 14-bit value as a float.
        """
        i = (128 * msb) + lsb
        if i >= 8192:
            i -= 16384
        return i * 0.00048828125
