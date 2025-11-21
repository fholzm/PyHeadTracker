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
    """Class for sending head tracking data to IEM SceneRotator via OSC.

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
        Send orientation data to the IEM SceneRotator.

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
        """Send orientation data to the IEM SceneRotator.

        Parameters
        ----------
        orientation : YPR | Quaternion
            The orientation data to send.
        """

        if isinstance(orientation, YPR):
            orientation = ypr2quat(orientation)

        if isinstance(orientation, Quaternion):
            w, x, y, z = orientation.inverse()
            self.client.send_message(self.OSC_address + "quaternions", [w, x, y, z])
        else:
            return


class IEMStereoEncoder(OutBase):
    """Class for sending head tracking data to IEM StereoEncoder via OSC.

    This class is used to transmit data via OSC to the IEM StereoEncoder of the IEM Plug-In Suite [1]. It supports sending orientation data in both YPR (Yaw, Pitch, Roll) and Quaternion formats. If Quaternion data is provided, it is automatically converted to YPR format before transmission.

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
        Send orientation data to the IEM StereoEncoder.

    References
    ----------
    [1] https://plugins.iem.at
    """

    def __init__(
        self,
        ip: str = "127.0.0.1",
        port: int = 8000,
        OSC_address: str = "/StereoEncoder/",
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
            The OSC address prefix for sending messages. Default is "/StereoEncoder/".
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
        """Send orientation data to the IEM StereoEncoder.

        Parameters
        ----------
        orientation : YPR | Quaternion
            The orientation data to send.
        """
        if not isinstance(orientation, (YPR, Quaternion)):
            return

        if isinstance(orientation, Quaternion):
            orientation = quat2ypr(orientation)

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

        self.client.send_message(self.OSC_address + "azimuth", y)
        self.client.send_message(self.OSC_address + "elevation", -p)
        self.client.send_message(self.OSC_address + "roll", r)


class IEMDirectivityShaper(OutBase):
    """Class for sending head tracking data to IEM DirectivityShaper via OSC.

    This class is used to transmit data via OSC to the IEM DirectivityShaper of the IEM Plug-In Suite [1]. It supports sending orientation data in both YPR (Yaw, Pitch, Roll) and Quaternion formats. If Quaternion data is provided, it is automatically converted to YPR format before transmission.

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
        Send orientation data to the IEM DirectivityShaper.

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
        """Send orientation data to the IEM DirectivityShaper.

        Parameters
        ----------
        orientation : YPR | Quaternion
            The orientation data to send.
        """
        if not isinstance(orientation, (YPR, Quaternion)):
            return

        if isinstance(orientation, Quaternion):
            orientation = quat2ypr(orientation)

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
        self.client.send_message(self.OSC_address + "probeElevation", -p)
        self.client.send_message(self.OSC_address + "probeRoll", r)


class IEMRoomEncoder(OutBase):
    """Class for sending head tracking data to IEM RoomEncoder via OSC.

    This class is used to transmit position via OSC to the IEM RoomEncoder of the IEM Plug-In Suite [1].

    Attributes
    ----------
    ip : str
        The IP address of the target application. Default is "127.0.0.1".
    port : int
        The port number of the target application. Default is 8000.
    OSC_address : str
        The OSC address prefix for sending messages. Default is "/RoomEncoder/listener" or "/RoomEncoder/source".
    offset_x : float
        Offset to be added to the x position. Default is 0.0.
    offset_y : float
        Offset to be added to the y position. Default is 0.0.
    offset_z : float
        Offset to be added to the z position. Default is 0.0.

    Methods
    -------
    send_position(position: Position)
        Send position data to the IEM RoomEncoder.

    References
    ----------
    [1] https://plugins.iem.at/docs/plugindescriptions/#roomencoder
    """

    def __init__(
        self,
        ip: str = "127.0.0.1",
        port: int = 8000,
        OSC_address: str = "/RoomEncoder/",
        mode: str = "listener",
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        offset_z: float = 0.0,
    ):
        """
        Parameters
        ----------
        ip : str
            The IP address of the target application. Default is "127.0.0.1".
        port : int
            The port number of the target application. Default is 8000.
        OSC_address : str
            The OSC address prefix for sending messages. Default is "/RoomEncoder/".
        mode: str
            Setting to control either the listener or source position.
            Possible values are "listener" or "source". Default is "listener".
        offset_x : float
            Offset to be added to the x position. Default is 0.0.
        offset_y : float
            Offset to be added to the y position. Default is 0.0.
        offset_z : float
            Offset to be added to the z position. Default is 0.0.
        """
        self.ip = ip
        self.port = port
        self.OSC_address = OSC_address
        self.client = SimpleUDPClient(self.ip, self.port)
        if mode.lower() in ["listener", "source"]:
            self.OSC_address += mode.lower()
        else:
            raise ValueError('mode must be either "listener" or "source"')
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z

    def send_position(self, position: Position):
        """Send position data to the IEM RoomEncoder.

        Parameters
        ----------
        position : Position
            The position data to send.
        """
        if not isinstance(position, Position):
            return

        x, y, z = position

        x += self.offset_x
        y += self.offset_y
        z += self.offset_z

        self.client.send_message(self.OSC_address + "X", x)
        self.client.send_message(self.OSC_address + "Y", y)
        self.client.send_message(self.OSC_address + "Z", z)


class SPARTA(OutBase):
    """Class for sending head tracking data to SPARTA Plug-Ins via OSC.

    This class is used to transmit data via OSC to the SPARTA applications [1]. It supports sending orientation data in both YPR (Yaw, Pitch, Roll) and Quaternion formats. If Quaternion data is provided, it is automatically converted to YPR format before transmission.

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

    Methods
    -------
    send_orientation(orientation: YPR | Quaternion | None)
        Send orientation data to SPARTA Plug-Ins.

    References
    ----------
    [1] https://leomccormack.github.io/sparta-site/

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
        """Send orientation data to SPARTA Plug-Ins.

        Parameters
        ----------
        orientation : YPR | Quaternion
            The orientation data to send.
        """
        if not isinstance(orientation, (YPR, Quaternion)):
            return

        if isinstance(orientation, Quaternion):
            orientation = quat2ypr(orientation)

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


class TASCAR(OutBase):
    """Class for sending head tracking data to TASCAR.

    This class is used to transmit data via OSC to TASCAR [1]. It supports sending orientation data in both YPR (Yaw, Pitch, Roll) and Quaternion formats. If Quaternion data is provided, it is automatically converted to YPR format before transmission.

    Attributes
    ----------
    OSC_address : str
        The OSC address prefix for sending messages, without tailing pos or zyxeuler.
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

    Methods
    -------
    send_orientation(orientation: YPR | Quaternion | None)
        Send orientation data to TASCAR.
    send_position(position: Position)
        Send position data to TASCAR.

    References
    ----------
    [1] https://tascar.org/
    """

    def __init__(
        self,
        OSC_address: str,
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
        OSC_address : str
            The OSC address prefix for sending messages, without tailing pos or zyxeuler.
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
        self.OSC_address_position = OSC_address.rstrip("/") + "/pos"
        self.OSC_address_orientation = OSC_address.rstrip("/") + "/zyxeuler"
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
        """Send orientation data to TASCAR.

        Parameters
        ----------
        orientation : YPR | Quaternion
            The orientation data to send.
        """
        if not isinstance(orientation, (YPR, Quaternion)):
            return

        if isinstance(orientation, Quaternion):
            orientation = quat2ypr(orientation)

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

        self.client.send_message(self.OSC_address_orientation, [y, p, r])

    def send_position(self, position: Position):
        """Send position data to TASCAR.

        Parameters
        ----------
        position : Position
            The position data to send.
        """
        if not isinstance(position, Position):
            return

        x, y, z = position

        self.client.send_message(self.OSC_address_position, [x, y, z])


# TODO: Implement generic OSC sender class?
