import xr
import numpy as np
from typing import Optional
from .dtypes import Quaternion, Position


class openXR:
    def __init__(
        self,
        context: xr.ContextObject,
        initial_pose: Optional[xr.Posef] = None,
        reset_pose: bool = False,
    ):
        """
        Initialize the HeadTracker class.
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
                initial_pose.orientation.x,
                initial_pose.orientation.y,
            ).inverse()

        self.reset_pose = reset_pose

    def read_raw_pose(self, frame_state: xr.FrameState):
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
            return views[xr.Eye.LEFT].pose
        else:
            return None

    def read_pose(self, frame_state: xr.FrameState):
        """
        Get the current head pose.
        """
        raw_pose = self.read_raw_pose(frame_state)

        if raw_pose is None:
            return None

        # Convert the raw pose to a Position and Quaternion
        # Note: OpenXR uses a right-handed coordinate system, so we need to adjust the
        # position and orientation accordingly.
        raw_position = Position(
            -raw_pose.position.z,
            -raw_pose.position.x,
            raw_pose.position.y,
        )
        raw_orientation = Quaternion(
            raw_pose.orientation.w,
            -raw_pose.orientation.z,
            raw_pose.orientation.x,
            raw_pose.orientation.y,
        )

        if self.reset_pose:
            # Reset the pose to the initial pose
            self.reference_position = raw_position
            self.reference_orientation_inv = raw_orientation.inverse()
            self.reset_pose = False

        # Get position and orientation relative to the initial pose
        new_position = self._adjust_position(raw_position)
        new_orientation = self._adjust_orientation(raw_orientation)

        return {"position": new_position, "orientation": new_orientation}

    def read_orientation(self, frame_state: xr.FrameState):
        """
        Get the current head orientation as a quaternion.
        """
        # Get the current time
        pose = self.read_pose(frame_state)

        if pose is not None:
            return pose["orientation"]
        else:
            return None

    def read_position(self, frame_state: xr.FrameState):
        """
        Get the current head position.
        """
        # Get the current time
        pose = self.read_pose(frame_state)
        if pose is not None:
            return pose["position"]
        else:
            return None

    def zero(self):
        """
        Reset the head tracker to the initial pose.
        """
        self.initial_pose = self.reset_pose = True

    def _adjust_orientation(self, current_orientation: Quaternion):
        # Multiply the current orientation by the inverse of the initial orientation
        return current_orientation * self.reference_orientation_inv

    def _adjust_position(self, current_position: Position):
        return current_position - self.reference_position
