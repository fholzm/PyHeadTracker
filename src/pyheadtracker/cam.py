"""
Access position and orientation data via webcam-based head tracking

Classes
- `MPFaceLandmarker`: Webcam-based head tracker using OpenCV and MediaPipe Face Landmarker
"""

from typing import Optional
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from .dtypes import Quaternion, YPR, Position, HTBase
from .utils import ypr2quat


class MPFaceLandmarker(HTBase):
    def __init__(
        self,
        cam_index: int = 0,
        model_weights: Optional[str] = None,
        orient_format: str = "q",
    ):
        """
        Parameters
        ----------
        camera_index : int
            The index of the webcam to use.
        model_weights : str, optional
            Path to custom model weights. If None, the default built-in model is used.
        orient_format : str
            The format for orientation data. Possible values are "q" (Quaternion) or "ypr" (Yaw, Pitch, Roll).
        """
        self.orient_format = orient_format
        self.cam_index = cam_index
        self.model_weights = (
            model_weights
            if model_weights is not None
            else "data/mediapipe-facelandmarker/face_landmarker_v2_with_blendshapes.task"
        )
        self.landmarker = None
        self.cap = None
        self.frame_count = 0

    def open(self):
        # Initialize MediaPipe Face Landmarker
        BaseOptions = python.BaseOptions(
            model_asset_path=self.model_weights,
        )
        FaceLandmarker = vision.FaceLandmarker
        FaceLandmarkerOptions = vision.FaceLandmarkerOptions
        VisionRunningMode = vision.RunningMode  # Correct import path

        # Load model (downloaded automatically)
        options = FaceLandmarkerOptions(
            base_options=BaseOptions,  # uses built-in model
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=True,
            num_faces=1,
            running_mode=VisionRunningMode.VIDEO,
        )

        self.landmarker = FaceLandmarker.create_from_options(options)
        self.cap = cv2.VideoCapture(self.cam_index)
        self.frame_count = 0

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.landmarker = None
        cv2.destroyAllWindows()

    def read_pose(self):
        if self.cap is None or self.landmarker is None:
            raise RuntimeError(
                "Camera is not opened. Call 'open()' before reading orientation."
            )

        ret, frame = self.cap.read()
        if not ret:
            return None

        # Convert to MediaPipe Image format
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
        )

        # Run detection with timestamp
        result = self.landmarker.detect_for_video(mp_image, self.frame_count)
        self.frame_count += 1

        if result.face_landmarks and result.facial_transformation_matrixes:
            # Get 4x4 pose transform matrix
            matrix = np.array(result.facial_transformation_matrixes[0].data).reshape(
                4, 4
            )

            # Extract rotation matrix (upper-left 3x3)
            rot_mat = matrix[:3, :3]
            translation = matrix[:3, 3]
            # TODO: Map relative translation coordinates to real-world units

            # --- Convert rotation matrix to yaw, pitch, roll ---
            sy = np.sqrt(rot_mat[0, 0] ** 2 + rot_mat[1, 0] ** 2)
            singular = sy < 1e-6

            if not singular:
                pitch = np.arctan2(rot_mat[2, 1], rot_mat[2, 2])
                yaw = np.arctan2(-rot_mat[2, 0], sy)
                roll = np.arctan2(rot_mat[1, 0], rot_mat[0, 0])
            else:
                pitch = np.arctan2(-rot_mat[1, 2], rot_mat[1, 1])
                yaw = 0
                roll = np.arctan2(rot_mat[0, 1], rot_mat[1, 1])

            orientation = YPR(yaw, pitch, roll)

            if self.orient_format == "q":
                orientation = ypr2quat(orientation)

            position = Position(translation[0], translation[1], translation[2])

            return {"position": position, "orientation": orientation}

    def read_orientation(self) -> YPR | Quaternion | None:
        pose = self.read_pose()
        if pose is None:
            return None
        return pose["orientation"]

    def read_position(self) -> Position | None:
        pose = self.read_pose()
        if pose is None:
            return None
        return pose["position"]

    def zero(self):
        # TODO: Implement zeroing functionality
        pass
