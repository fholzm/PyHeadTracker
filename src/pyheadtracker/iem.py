import mido
import numpy as np


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
            self.midi_input = mido.open_input(self.device_name)
        except IOError as e:
            raise RuntimeError(
                f"Could not open MIDI input device '{self.device_name}': {e}"
            )
        self.inport = None

    def open(self):
        """Open the MIDI input device and start reading orientation data."""
        self.inport = mido.open_input(self.device_name)

    def close(self):
        """Close the MIDI input device and stop reading orientation data."""
        if self.inport is not None:
            self.inport.close()
        self.inport = None

    def read_orientation(self):
        """Read orientation data from the MIDI device."""

        if self.inport is None:
            raise RuntimeError("MIDI input device is not open.")

        n_messages = 8 if self.orient_format == "q" else 6
        msg_list = []
        # Catch last n_messages
        for current_msg in self.inport.iter_pending():
            msg_list.append(current_msg)
            if len(msg_list) > n_messages:
                break

        return self._process_message(msg_list)

    def _process_message(self, msg_list):
        """Process incoming MIDI messages."""
        orientation = {
            "w_lsb": -1,
            "x_lsb": -1,
            "y_lsb": -1,
            "z_lsb": -1,
            "w_msb": -1,
            "x_msb": -1,
            "y_msb": -1,
            "z_msb": -1,
        }
        for msg in msg_list:
            if msg.type == "control_change":
                if msg.control == 48 and orientation["w_lsb"] == -1:
                    orientation["w_lsb"] = msg.value
                elif msg.control == 49 and orientation["x_lsb"] == -1:
                    orientation["x_lsb"] = msg.value
                elif msg.control == 50 and orientation["y_lsb"] == -1:
                    orientation["y_lsb"] = msg.value
                elif msg.control == 51 and orientation["z_lsb"] == -1:
                    orientation["z_lsb"] = msg.value

                elif msg.control == 16 and orientation["w_msb"] == -1:
                    orientation["w_msb"] = msg.value
                elif msg.control == 17 and orientation["x_msb"] == -1:
                    orientation["x_msb"] = msg.value
                elif msg.control == 18 and orientation["y_msb"] == -1:
                    orientation["y_msb"] = msg.value
                elif msg.control == 19 and orientation["z_msb"] == -1:
                    orientation["z_msb"] = msg.value

        if (
            orientation["w_lsb"] != -1
            and orientation["x_lsb"] != -1
            and orientation["y_lsb"] != -1
        ):
            w = (((orientation["w_msb"] * 128) + orientation["w_lsb"]) / 8192.0) - 1
            x = (((orientation["x_msb"] * 128) + orientation["x_lsb"]) / 8192.0) - 1
            y = (((orientation["y_msb"] * 128) + orientation["y_lsb"]) / 8192.0) - 1

            if self.orient_format == "ypr":
                return np.array([y, x, w])

            if orientation["z_msb"] != -1 and orientation["z_lsb"] != -1:
                z = (((orientation["z_msb"] * 128) + orientation["z_lsb"]) / 8192.0) - 1
                return np.array([w, x, y, z])

        # If we reach here, no valid orientation data was found
        return np.array([])
