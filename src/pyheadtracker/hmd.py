import xr
import numpy as np


class openXR:
    def __init__(
        self,
        context: xr.ContextObject,
        initial_pose: xr.Posef = None,
        reset_pose: bool = False,
    ):
        """
        Initialize the HeadTracker class.
        """
        self.context = context
        self.initial_pose = (
            initial_pose
            if initial_pose is not None
            else xr.Posef(
                position=xr.Vector3f(0.0, 0.0, 0.0),
                orientation=xr.Quaternionf(1.0, 0.0, 0.0, 0.0),
            )
        )
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

        if self.reset_pose:
            # Reset the pose to the initial pose
            self.initial_pose = raw_pose
            self.reset_pose = False

        # Get position and orientation relative to the initial pose
        new_position = self._adjust_position(raw_pose.position)
        new_orientation = self._adjust_orientation(raw_pose.orientation)

        # Maniulate axes to match the expected coordinate system
        new_position = np.array([-new_position.z, -new_position.x, new_position.y])
        new_orientation = np.array(
            [
                new_orientation.w,
                -new_orientation.z,
                new_orientation.x,
                new_orientation.y,
            ]
        )

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

    def _invert_quaternion(self, q):
        return xr.Quaternionf(w=q.w, x=-q.x, y=-q.y, z=-q.z)

    def _multiply_quaternions(self, q1, q2):
        return xr.Quaternionf(
            w=q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z,
            x=q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y,
            y=q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x,
            z=q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w,
        )

    def _adjust_orientation(self, current_orientation: xr.Quaternionf):
        # Compute the inverse of the initial orientation
        initial_inverse = self._invert_quaternion(self.initial_pose.orientation)
        # Multiply the current orientation by the inverse of the initial orientation
        return self._multiply_quaternions(current_orientation, initial_inverse)
        # return current_orientation

    def _adjust_position(self, current_position: xr.Vector3f):
        return xr.Vector3f(
            x=current_position.x - self.initial_pose.position.x,
            y=current_position.y - self.initial_pose.position.y,
            z=current_position.z - self.initial_pose.position.z,
        )
