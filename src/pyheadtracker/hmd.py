"""
Accessing position and orientation data from head mounted displays (HMDs).

Due to pyopenxr not being available on macOS, this module is only available on Windows and Linux.

Classes:
- `openXR`: A class for accessing position and orientation data from OpenXR-compatible HMDs, relying on the pyopenxr library
"""

import xr
from xr.utils.gl import ContextObject
from typing import Optional
from .dtypes import Quaternion, YPR, Position, HTBase
from .utils import quat2ypr


class openXR(HTBase):
    """
    A class for accessing position and orientation data from OpenXR-compatible HMDs.

    This class uses the pyopenxr library to read the head pose data from the HMD. Upon request, the position and orientation is returned.

    Attributes
    ----------
    context : ContextObject
        The OpenXR context object.
    reference_position : Position
        A reference position, where the tracking data can be normalized to.
    reference_orientation_inv : Quaternion
        The inverse of the reference orientation, used to normalize the orientation data.
    reset_position : bool
        A flag to indicate if the position should be reset to the reference position.
    reset_orientation : bool
        A flag to indicate if the orientation should be reset to the reference orientation.
    orient_format : str
        The format of the orientation data. Internally, Quaternions are used. Possible values are "ypr" (Yaw, Pitch, Roll) or "q" (Quaternion). Default is "q".

    Methods
    -------
    read_raw_pose(frame_state: xr.FrameState) -> xr.Posef or None
        Returns if available the raw pose data from the HMD without any adjustments in the openXR coordinate system definition.
    read_pose(frame_state: xr.FrameState) -> dict or None
        Returns if available the adjusted position and orientation data from the HMD. The dictionary contains a Position and Quaternion object.
    read_orientation(frame_state: xr.FrameState) -> Quaternion or None
        Returns if available the current head orientation as a Quaternion object.
    read_position(frame_state: xr.FrameState) -> Position or None
        Returns if available the current head position as a Position object.
    zero()
        Resets the position and orientation to the reference values.
    zero_orientation()
        Resets the orientation to the reference orientation.
    zero_position()
        Resets the position to the reference position.
    """

    def __init__(
        self,
        context: ContextObject,
        initial_pose: Optional[xr.Posef] = None,
        reset_position: bool = False,
        reset_orientation: bool = False,
        orient_format: str = "q",
    ):
        """
        Parameters
        ----------
        context : ContextObject
            The OpenXR context object.
        initial_pose : xr.Posef, optional
            The initial pose of the HMD. If not provided, the position will be set to (0, 0, 0) and the orientation to the identity quaternion.
        reset_position : bool, optional
            If True, the position will be reset to the initial pose when read_pose is called. Default is False.
        reset_orientation : bool, optional
            If True, the orientation will be reset to the initial pose when read_pose is called. Default is False.
        orient_format : str, optional
            The format of the orientation data. Possible values are "ypr" (Yaw, Pitch, Roll) or "q" (Quaternion). Default is "q".
        """
        self.context = context

        if initial_pose is None:
            self.reference_position = Position(0.0, 0.0, 0.0)
            self.reference_orientation_inv = Quaternion(1.0, 0.0, 0.0, 0.0).inverse()
        else:
            self.reference_position = Position(
                -initial_pose.position.z,
                -initial_pose.position.x,
                initial_pose.position.y,
            )
            self.reference_orientation_inv = Quaternion(
                initial_pose.orientation.w,
                -initial_pose.orientation.z,
                -initial_pose.orientation.x,
                initial_pose.orientation.y,
            ).inverse()

        self.reset_position = reset_position
        self.reset_orientation = reset_orientation

        assert orient_format in [
            "ypr",
            "q",
        ], "Orientation format must be 'ypr' or 'q'"

        self.orient_format = orient_format

    def read_raw_pose(self, frame_state: xr.FrameState):
        """
        Get the raw pose data from the HMD without any adjustments in the OpenXR coordinate system definition.

        Parameters
        ----------
        frame_state : xr.FrameState
            The current frame state from OpenXR.

        Returns
        -------
        xr.Posef or None
            The raw pose data from the HMD, or None if the pose is not available.
        """

        view_state, views = xr.locate_views(
            session=self.context.session,
            view_locate_info=xr.ViewLocateInfo(
                view_configuration_type=self.context.view_configuration_type,
                display_time=frame_state.predicted_display_time,
                space=self.context.space,
            ),
        )

        flags = xr.ViewStateFlags(view_state.view_state_flags)
        if flags & xr.ViewStateFlags.POSITION_VALID_BIT:
            return views[xr.utils.Eye.LEFT.value].pose
        else:
            return None

    def read_pose(self, frame_state: xr.FrameState):
        """
        Read and post-process the current head pose.

        Get the current head position and orientation as a dictionary containing Position and Quaternion objects. The position and orientation are adjusted relative to the initial pose.

        Parameters
        ----------
        frame_state : xr.FrameState
            The current frame state from OpenXR.

        Returns
        -------
        dict or None
            A dictionary containing the adjusted position and orientation, or None if the pose is not available.
        """
        raw_pose = self.read_raw_pose(frame_state)

        if raw_pose is None:
            return None

        # Convert the raw pose to a Position and Quaternion
        # Note: OpenXR uses a right-handed coordinate system as often used in 3D graphics, so we need to adjust the position and orientation accordingly for audio applications.
        raw_position = Position(
            -raw_pose.position.z,
            -raw_pose.position.x,
            raw_pose.position.y,
        )
        raw_orientation = Quaternion(
            raw_pose.orientation.w,
            -raw_pose.orientation.z,
            -raw_pose.orientation.x,
            raw_pose.orientation.y,
        )

        if self.reset_position:
            # Reset the position to zero
            self.reference_position = raw_position
            self.reset_position = False
        if self.reset_orientation:
            # Reset the orientation
            self.reference_orientation_inv = raw_orientation.inverse()
            self.reset_orientation = False

        # Get position and orientation relative to the initial pose
        new_position = self.__adjust_position(raw_position)
        new_orientation = self.__adjust_orientation(raw_orientation)

        if self.orient_format == "ypr":
            new_orientation = quat2ypr(new_orientation)

        return {"position": new_position, "orientation": new_orientation}

    def read_orientation(self, frame_state: xr.FrameState):
        """
        Get the current head orientation as a Quaternion.

        Parameters
        ----------
        frame_state : xr.FrameState
            The current frame state from OpenXR.

        Returns
        -------
        Quaternion or None
            The current head orientation as a Quaternion object, or None if the pose is not available.
        """
        pose = self.read_pose(frame_state)

        if pose is not None:
            return pose["orientation"]
        else:
            return None

    def read_position(self, frame_state: xr.FrameState):
        """
        Get the current head position as a Position object.

        Parameters
        ----------
        frame_state : xr.FrameState
            The current frame state from OpenXR.

        Returns
        -------
        Position or None
            The current head position as a Position object, or None if the pose is not available.
        """
        pose = self.read_pose(frame_state)
        if pose is not None:
            return pose["position"]
        else:
            return None

    def zero(self):
        """
        Reset reference position and orientation to the current one.
        """
        self.reset_position = True
        self.reset_orientation = True

    def zero_orientation(self):
        """
        Reset reference orientation to the current one.
        """
        self.reset_orientation = True

    def zero_position(self):
        """
        Reset reference position to the current one.
        """
        self.reset_position = True

    def __adjust_orientation(self, current_orientation: Quaternion):
        return current_orientation * self.reference_orientation_inv

    def __adjust_position(self, current_position: Position):
        return current_position - self.reference_position
