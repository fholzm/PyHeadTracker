"""
Module for interacting with DIY head trackers.

Modules:
- `MrHeadTracker`: A class for reading orientation data from the IEM MrHeadTracker device via MIDI.
"""

import mido
import time
import numpy as np
from .dtypes import Quaternion, YPR


class MrHeadTracker:
    """
    Class for interacting with the IEM MrHeadTracker.

    The IEM MrHeadTracker is a DIY head tracker that sends orientation data via ordinary MIDI control messages. It is based on an Arduino/Teensy and the BNO055 or BNO085 sensor. Code, Wiki, and schematics are openly accessible [1].

    Attributes
    ----------
    device_name : str
        The name of the MIDI device to connect to.
    orient_format : str
        The format for orientation data. Possible values are "q" (Quaternion) or "ypr" (Yaw, Pitch, Roll).
    inport : mido.Input
        The MIDI input port for reading data. This attribute is initialized to `None` and set when the `open()` method is called.
    ready : bool
        Internal state - indicates whether the tracker is ready to read data.
    setted_bytes : int
        Internal state - The number of bytes that have been set in the orientation data.
    orientation_bytes : dict
        Internal state - A dictionary to hold the raw bytes of the orientation data.

    Methods
    -------
    open()
        Opens the MIDI input port.
    close()
        Closes the MIDI input port gracefully.
    read_orientation()
        Reads the orientation data from the MIDI device and returns it in the specified format (Quaternion or YPR).

    Raises
    ------
    RuntimeError
        If the specified MIDI device cannot be opened or does not exist. Make sure the device is connected and the name is correct. On Windows, only exclusive connections to MIDI devices are possible, so ensure no other application is using the device.

    References
    ----------
    [1] https://git.iem.at/DIY/MrHeadTracker
    """

    def __init__(self, device_name: str = "MrHeadTracker", orient_format: str = "q"):
        """
        Parameters
        ----------
        device_name : str
            The name of the MIDI device to connect to. Default is "MrHeadTracker".
        orient_format : str
            The format for orientation data. Must correspond to the hardware settings if using the first version. Later versions only send quaternions. Possible values are "q" (Quaternion) or "ypr" (Yaw, Pitch, Roll). Default is "q".

        Raises
        ------
        RuntimeError
            If the specified MIDI device cannot be opened or does not exist. Make sure the device is connected and the name is correct. On Windows, only exclusive connections to MIDI devices are possible, so ensure no other application is using the device.
        """

        self.device_name = device_name

        # Set orient format
        assert orient_format in ["q", "ypr"], "Orientation format must be 'q' or 'ypr'"
        self.orient_format = orient_format

        # Check if the device is available
        try:
            with mido.open_input(self.device_name) as inport:
                pass
        except IOError as e:
            raise RuntimeError(
                f"Could not open MIDI input device '{self.device_name}': {e} \nAvailable devices: {mido.get_input_names()}"
            )

        # Initialize internal states
        self.inport = None
        self.ready = False
        self.setted_bytes = 0
        self.orientation_bytes = {
            "w_lsb": np.nan,
            "x_lsb": np.nan,
            "y_lsb": np.nan,
            "z_lsb": np.nan,
            "w_msb": np.nan,
            "x_msb": np.nan,
            "y_msb": np.nan,
            "z_msb": np.nan,
        }

    def open(self):
        """Open the MIDI input port."""
        if self.inport is None:
            self.inport = mido.open_input(self.device_name)

    def close(self):
        """Close the MIDI input port."""
        if self.inport is not None:
            self.inport.close()
            self.inport = None

    def read_orientation(self):
        """Read orientation data from the MIDI device.

        Returns
        -------
        Quaternion, YPR, or None
            The orientation data in the specified format (Quaternion or YPR). Returns None if no data is available.
        """

        assert (
            self.inport is not None
        ), "MIDI input port is not open. Call open() first."

        self.ready = False

        # Determine, how many bytes of data we expect
        required_bytes = 8 if self.orient_format == "q" else 6

        t_start = time.time()

        # Collect messages until we have all bytes
        for msg in self.inport:
            self.__decode_message(msg)

            # If we have all bytes, break
            if self.setted_bytes == required_bytes:
                self.setted_bytes = 0
                self.ready = True
                break

            # Break also if we don't receive enough messages
            if time.time() - t_start > 0.25:
                return None

        return self.__process_message()

    def __decode_message(self, msg):
        """Decode incoming MIDI messages and extract orientation data."""

        if msg.type == "control_change":
            if msg.control == 48 and self.orientation_bytes["w_lsb"] is np.nan:
                self.orientation_bytes["w_lsb"] = msg.value
                self.setted_bytes += 1
            elif msg.control == 49 and self.orientation_bytes["x_lsb"] is np.nan:
                self.orientation_bytes["x_lsb"] = msg.value
                self.setted_bytes += 1
            elif msg.control == 50 and self.orientation_bytes["y_lsb"] is np.nan:
                self.orientation_bytes["y_lsb"] = msg.value
                self.setted_bytes += 1
            elif (
                msg.control == 51
                and self.orientation_bytes["z_lsb"] is np.nan
                and self.orient_format == "q"
            ):
                self.orientation_bytes["z_lsb"] = msg.value
                self.setted_bytes += 1

            elif msg.control == 16 and self.orientation_bytes["w_msb"] is np.nan:
                self.orientation_bytes["w_msb"] = msg.value
                self.setted_bytes += 1
            elif msg.control == 17 and self.orientation_bytes["x_msb"] is np.nan:
                self.orientation_bytes["x_msb"] = msg.value
                self.setted_bytes += 1
            elif msg.control == 18 and self.orientation_bytes["y_msb"] is np.nan:
                self.orientation_bytes["y_msb"] = msg.value
                self.setted_bytes += 1
            elif (
                msg.control == 19
                and self.orientation_bytes["z_msb"] is np.nan
                and self.orient_format == "q"
            ):
                self.orientation_bytes["z_msb"] = msg.value
                self.setted_bytes += 1

    def __process_message(self):
        """Process incoming MIDI messages."""

        if not self.ready:
            return None

        w = (
            ((self.orientation_bytes["w_msb"] * 128) + self.orientation_bytes["w_lsb"])
            / 8192.0
        ) - 1
        x = (
            ((self.orientation_bytes["x_msb"] * 128) + self.orientation_bytes["x_lsb"])
            / 8192.0
        ) - 1
        y = (
            ((self.orientation_bytes["y_msb"] * 128) + self.orientation_bytes["y_lsb"])
            / 8192.0
        ) - 1

        if self.orient_format == "ypr":
            out = YPR(w * np.pi, x * np.pi, y * np.pi, "ypr")

        else:
            z = (
                (
                    (self.orientation_bytes["z_msb"] * 128)
                    + self.orientation_bytes["z_lsb"]
                )
                / 8192.0
            ) - 1
            out = Quaternion(w, x, y, z)

        # Reset the bytes for the next message
        for key in self.orientation_bytes:
            self.orientation_bytes[key] = np.nan

        self.ready = False

        return out
