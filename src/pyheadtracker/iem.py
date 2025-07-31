import mido
import time
import numpy as np
from .dtypes import Quaternion, YPR


class MrHeadTracker:
    """Class for interacting with MrHeadTracker.

    Attributes:
        device_name (str): The name of the MIDI device to connect to.
        orient_format (str): The format for orientation data. Possible values are "q" (Quaternion) or "ypr" (Yaw, Pitch, Roll).
    """

    def __init__(self, device_name: str = "MrHeadTracker", orient_format: str = "q"):
        self.device_name = device_name

        assert orient_format in ["q", "ypr"], "Orientation format must be 'q' or 'ypr'"

        self.orient_format = orient_format

        try:
            with mido.open_input(self.device_name) as inport:
                pass
        except IOError as e:
            raise RuntimeError(
                f"Could not open MIDI input device '{self.device_name}': {e} \nAvailable devices: {mido.get_input_names()}"
            )

        self.inport = None

        self.ready = False

        self.setted_bytes = 0

        # Initialize the individual bytes
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
        """Read orientation data from the MIDI device."""

        assert (
            self.inport is not None
        ), "MIDI input port is not open. Call open() first."

        self.ready = False
        n_messages = 8 if self.orient_format == "q" else 6

        t_start = time.time()

        # Collect messages until we have all bytes
        for msg in self.inport:
            self.__decode_message(msg)

            # If we have all bytes, break
            if self.setted_bytes == n_messages:
                self.setted_bytes = 0
                self.ready = True
                break

            # Break also if we don't receive enough messages
            if time.time() - t_start > 0.25:
                return None

        return self.__process_message()

    def __decode_message(self, msg):
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
