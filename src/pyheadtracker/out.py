"""Module for sending head tracking data to various target applications.

Modules:
- `IEMSceneRotator`: Class to send data to IEM Scene Rotator via OSC.
"""

from pythonosc.udp_client import SimpleUDPClient
from abc import abstractmethod
import warnings
from .dtypes import YPR, Quaternion, Position
from .utils import ypr2quat, quat2ypr


class OutBase:
    """Base class for outputting data to a target application.

    Methods
    -------
    send_orientation(orientation: YPR | Quaternion)
        Send orientation data to the desired target application.
    send_position(position: Position)
        Send position data to the desired target application.
    """

    @abstractmethod
    def send_orientation(self, orientation: YPR | Quaternion):
        """Send orientation data to the desired target application.

        Parameters
        ----------
        orientation : YPR | Quaternion
            The orientation data to send.
        """
        warnings.warn("send_orientation method not implemented.", UserWarning)
        pass

    @abstractmethod
    def send_position(self, position: Position):
        """Send position data to the desired target application.

        Parameters
        ----------
        position : Position
            The position data to send.
        """
        warnings.warn("send_position method not implemented.", UserWarning)
        pass


class IEMSceneRotator(OutBase):
    """Class for sending head tracking data to IEM Scene Rotator via OSC.

    This class is used to transmit data via OSC to the IEM SceneRotator of the IEM Plug-In Suite [1]. It supports sending orientation data in both YPR (Yaw, Pitch, Roll) and Quaternion formats. If YPR data is provided, it is automatically converted to Quaternion format before transmission.

    Attributes
    ----------
    ip : str
        The IP address of the target application. Default is "127.0.0.1".
    port : int
        The port number of the target application. Default is 8000.
    OSC_address : str
        The OSC address prefix for sending messages. Default is "/SceneRotator/".

    Methods
    -------
    send_orientation(orientation: YPR | Quaternion | None)
        Send orientation data to the IEM Scene Rotator.

    References
    ----------
    [1] https://plugins.iem.at
    """

    def __init__(
        self,
        ip: str = "127.0.0.1",
        port: int = 8000,
        OSC_address: str = "/SceneRotator/",
    ):
        """
        Parameters
        ----------
        ip : str
            The IP address of the target application. Default is "127.0.0.1".
        port : int
            The port number of the target application. Default is 8000.
        OSC_address : str
            The OSC address prefix for sending messages. Default is "/SceneRotator/".
        """
        self.ip = ip
        self.port = port
        self.OSC_address = OSC_address
        self.client = SimpleUDPClient(self.ip, self.port)

    def send_orientation(self, orientation: YPR | Quaternion | None):
        """Send orientation data to the IEM Scene Rotator.

        Parameters
        ----------
        orientation : YPR | Quaternion
            The orientation data to send.
        """
        if isinstance(orientation, Quaternion):
            w, x, y, z = orientation
            self.client.send_message(self.OSC_address + "quaternions", [w, -y, x, -z])

        elif isinstance(orientation, YPR):
            y, p, r = orientation.to_degrees()
            self.client.send_message(self.OSC_address + "yaw", -y)
            self.client.send_message(self.OSC_address + "pitch", p)
            self.client.send_message(self.OSC_address + "roll", -r)
        else:
            return


class IEMDirectivityShaper(OutBase):
    """Class for sending head tracking data to IEM Directivity Shaper via OSC.

    This class is used to transmit data via OSC to the IEM Directivity Shaper of the IEM Plug-In Suite [1]. It supports sending orientation data in both YPR (Yaw, Pitch, Roll) and Quaternion formats. If Quaternion data is provided, it is automatically converted to YPR format before transmission.

    Attributes
    ----------
    ip : str
        The IP address of the target application. Default is "127.0.0.1".
    port : int
        The port number of the target application. Default is 8000.
    OSC_address : str
        The OSC address prefix for sending messages. Default is "/DirectivityShaper/".
    offset_az : float
        Offset in degrees to be added to the azimuth (yaw) angle. Default is 0.0.
    offset_el : float
        Offset in degrees to be added to the elevation (pitch) angle. Default is 0.0.
    offset_roll : float
        Offset in degrees to be added to the roll angle. Default is 0.0.
    invert_az : bool
        If True, invert the azimuth (yaw) angle. Default is False.
    invert_el : bool
        If True, invert the elevation (pitch) angle. Default is False.
    invert_roll : bool
        If True, invert the roll angle. Default is False.

    Methods
    -------
    send_orientation(orientation: YPR | Quaternion | None)
        Send orientation data to the IEM Directivity Shaper.

    References
    ----------
    [1] https://plugins.iem.at
    """

    def __init__(
        self,
        ip: str = "127.0.0.1",
        port: int = 8000,
        OSC_address: str = "/DirectivityShaper/",
        offset_az: float = 0.0,
        offset_el: float = 0.0,
        offset_roll: float = 0.0,
        invert_az: bool = False,
        invert_el: bool = False,
        invert_roll: bool = False,
    ):
        """
        Parameters
        ----------
        ip : str
            The IP address of the target application. Default is "127.0.0.1".
        port : int
            The port number of the target application. Default is 8000.
        OSC_address : str
            The OSC address prefix for sending messages. Default is "/SceneRotator/".
        offset_az : float
            Offset in degrees to be added to the azimuth (yaw) angle. Default is 0.0.
        offset_el : float
            Offset in degrees to be added to the elevation (pitch) angle. Default is 0.0.
        offset_roll : float
            Offset in degrees to be added to the roll angle. Default is 0.0.
        invert_az : bool
            If True, invert the azimuth (yaw) angle. Default is False.
        invert_el : bool
            If True, invert the elevation (pitch) angle. Default is False.
        invert_roll : bool
            If True, invert the roll angle. Default is False.
        """
        self.ip = ip
        self.port = port
        self.OSC_address = OSC_address
        self.client = SimpleUDPClient(self.ip, self.port)
        self.offset_az = offset_az
        self.offset_el = offset_el
        self.offset_roll = offset_roll
        self.invert_az = invert_az
        self.invert_el = invert_el
        self.invert_roll = invert_roll

        # Engage probe lock
        self.client.send_message(self.OSC_address + "probeLock", 1.0)

    def send_orientation(self, orientation: YPR | Quaternion | None):
        """Send orientation data to the IEM Scene Rotator.

        Parameters
        ----------
        orientation : YPR | Quaternion
            The orientation data to send.
        """
        if not isinstance(orientation, (YPR, Quaternion)):
            return

        if isinstance(orientation, Quaternion):
            orientation = quat2ypr(orientation)

        # TODO: Check for correct sign and range of angles
        y, p, r = orientation.to_degrees()

        y += self.offset_az
        p += self.offset_el
        r += self.offset_roll

        if self.invert_az:
            y = -y
        if self.invert_el:
            p = -p
        if self.invert_roll:
            r = -r

        self.client.send_message(self.OSC_address + "probeAzimuth", y)
        self.client.send_message(self.OSC_address + "probeElevation", p)
        self.client.send_message(self.OSC_address + "probeRoll", r)


# TODO: Implement RoomEncoder


class SPARTA(OutBase):
    """Class for sending head tracking data to SPARTA AmbiBin via OSC.

    This class is used to transmit data via OSC to the SPARTA AmbiBin application [1]. It supports sending orientation data in both YPR (Yaw, Pitch, Roll) and Quaternion formats. If Quaternion data is provided, it is automatically converted to YPR format before transmission.

    Attributes
    ----------
    ip : str
        The IP address of the target application. Default is "127.0.0.1".
    port : int
        The port number of the target application. Default is 9000.
    offset_az : float
        Offset in degrees to be added to the azimuth (yaw) angle. Default is 0.0.
    offset_el : float
        Offset in degrees to be added to the elevation (pitch) angle. Default is 0.0.
    offset_roll : float
        Offset in degrees to be added to the roll angle. Default is 0.0.
    invert_az : bool
        If True, invert the azimuth (yaw) angle. Default is False.
    invert_el : bool
        If True, invert the elevation (pitch) angle. Default is False.
    invert_roll : bool
        If True, invert the roll angle. Default is False.
    """

    def __init__(
        self,
        ip: str = "127.0.0.1",
        port: int = 9000,
        offset_az: float = 0.0,
        offset_el: float = 0.0,
        offset_roll: float = 0.0,
        invert_az: bool = False,
        invert_el: bool = False,
        invert_roll: bool = False,
    ):
        """
        Parameters
        ----------
        ip : str
            The IP address of the target application. Default is "127.0.0.1".
        port : int
            The port number of the target application. Default is 9000.
        offset_az : float
            Offset in degrees to be added to the azimuth (yaw) angle. Default is 0.0.
        offset_el : float
            Offset in degrees to be added to the elevation (pitch) angle. Default is 0.0.
        offset_roll : float
            Offset in degrees to be added to the roll angle. Default is 0.0.
        invert_az : bool
            If True, invert the azimuth (yaw) angle. Default is False.
        invert_el : bool
            If True, invert the elevation (pitch) angle. Default is False.
        invert_roll : bool
            If True, invert the roll angle. Default is False.
        """
        self.ip = ip
        self.port = port
        self.client = SimpleUDPClient(self.ip, self.port)
        self.offset_az = offset_az
        self.offset_el = offset_el
        self.offset_roll = offset_roll
        self.invert_az = invert_az
        self.invert_el = invert_el
        self.invert_roll = invert_roll

    def send_orientation(self, orientation: YPR | Quaternion | None):
        """Send orientation data to the IEM Scene Rotator.

        Parameters
        ----------
        orientation : YPR | Quaternion
            The orientation data to send.
        """
        if not isinstance(orientation, (YPR, Quaternion)):
            return

        if isinstance(orientation, Quaternion):
            orientation = quat2ypr(orientation)

        # TODO: Check for correct sign and range of angles
        y, p, r = orientation.to_degrees()

        y += self.offset_az
        p += self.offset_el
        r += self.offset_roll

        if self.invert_az:
            y = -y
        if self.invert_el:
            p = -p
        if self.invert_roll:
            r = -r

        self.client.send_message("/ypr", [y, p, r])


# TODO: Implement TASCAR
# TODO: Implement generic OSC sender class?
