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
        landmark_points_idx: Optional[list[int]] = None,
        landmark_points_3d: Optional[np.ndarray] = None,
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
        if landmark_points_idx is None:
            self.landmark_points_idx = [1, 152, 33, 263, 61, 291]
        else:
            self.landmark_points_idx = landmark_points_idx

        if landmark_points_3d is None:
            self.landmark_points_3d = np.array(
                [
                    [0.0, 0.0, 0.0],  # Nose tip (1)
                    [0.0, -0.063, -0.033],  # Chin (152)
                    [-0.043, 0.032, -0.026],  # Left eye outer corner (33)
                    [0.043, 0.032, -0.026],  # Right eye outer corner (263)
                    [-0.028, -0.028, -0.025],  # Left mouth corner (61)
                    [0.028, -0.028, -0.025],  # Right mouth corner (291)
                ],
                dtype=np.float64,
            )
        else:
            self.landmark_points_3d = landmark_points_3d

        assert (
            len(self.landmark_points_idx) == self.landmark_points_3d.shape[0]
        ), "Length of landmark_points_idx must match number of rows in landmark_points_3d"

        self.landmarker = None
        self.cap = None
        self.frame_count = 0
        self.frame_width = 0
        self.frame_height = 0
        self.focal_length = 0

        self.camera_matrix = None
        self.dist_coeffs = None

        self.initial_rotation_matrix = None
        self.initial_R = None
        self.initial_tvec = None

        self.reset_orientation = True
        self.reset_position = True

        self.is_opened = False

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

        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.focal_length = self.frame_width
        self.camera_matrix = np.array(
            [
                [self.focal_length, 0, self.frame_width / 2],
                [0, self.focal_length, self.frame_height / 2],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )
        self.dist_coeffs = np.zeros((4, 1))

        self.is_opened = True

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.landmarker = None
            self.is_opened = False
        cv2.destroyAllWindows()

    def read_orientation(self) -> YPR | Quaternion | None:
        pose = self.__read_pose_internal(calculate_orientation=True)
        if pose is None or pose["orientation"] is None:
            return None
        return pose["orientation"]

    def read_position(self) -> Position | None:
        pose = self.__read_pose_internal(calculate_position=True)
        if pose is None or pose["position"] is None:
            return None
        return pose["position"]

    def read_pose(self) -> dict[str, Position | Quaternion | YPR] | None:
        pose = self.__read_pose_internal(
            calculate_orientation=True, calculate_position=True
        )
        if pose is None:
            return None
        return pose

    def zero(self):
        self.reset_orientation = True
        self.reset_position = True

    def zero_orientation(self):
        self.reset_orientation = True

    def zero_position(self):
        self.reset_position = True

    def __read_pose_internal(
        self, calculate_orientation: bool = False, calculate_position: bool = False
    ):

        if not self.is_opened:
            raise RuntimeError(
                "Camera is not opened. Call 'open()' before reading orientation."
            )

        ret, frame = self.cap.read()
        if not ret:
            return None

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
        )
        result = self.landmarker.detect_for_video(mp_image, self.frame_count)
        self.frame_count += 1

        tmp_orientation = None
        tmp_position = None

        if calculate_orientation and result.facial_transformation_matrixes:
            transformation_matrix = np.array(
                result.facial_transformation_matrixes[0].data
            ).reshape(4, 4)

            # Extract rotation matrix and translation vector
            rotation_matrix = transformation_matrix[:3, :3]

            if self.initial_rotation_matrix is None or self.reset_orientation:
                self.initial_rotation_matrix = rotation_matrix.copy()
                self.reset_orientation = False

            # Calculate relative rotation matrix
            relative_rotation_matrix = rotation_matrix @ self.initial_rotation_matrix.T
            # --- Convert rotation matrix to yaw, pitch, roll ---
            sy = np.sqrt(
                relative_rotation_matrix[0, 0] ** 2
                + relative_rotation_matrix[1, 0] ** 2
            )
            singular = sy < 1e-6

            if not singular:
                pitch = np.arctan2(
                    relative_rotation_matrix[2, 1], relative_rotation_matrix[2, 2]
                )
                yaw = np.arctan2(-relative_rotation_matrix[2, 0], sy)
                roll = np.arctan2(
                    relative_rotation_matrix[1, 0], relative_rotation_matrix[0, 0]
                )
            else:
                pitch = np.arctan2(
                    -relative_rotation_matrix[1, 2], relative_rotation_matrix[1, 1]
                )
                yaw = 0
                roll = np.arctan2(
                    relative_rotation_matrix[0, 1], relative_rotation_matrix[1, 1]
                )

            tmp_orientation = (
                YPR(yaw, pitch, roll)
                if self.orient_format == "ypr"
                else ypr2quat(YPR(yaw, pitch, roll))
            )

        if calculate_position and result.face_landmarks:
            # Extract 2D image points
            face_landmarks = result.face_landmarks[0]
            image_points = np.array(
                [
                    [
                        face_landmarks[idx].x * self.frame_width,
                        face_landmarks[idx].y * self.frame_height,
                    ]
                    for idx in self.landmark_points_idx
                ],
                dtype=np.float64,
            )

            # Solve PnP
            success, rvec, tvec = cv2.solvePnP(
                self.landmark_points_3d,
                image_points,
                self.camera_matrix,
                self.dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE,
            )

            if success:
                if self.initial_R is None or self.reset_position:
                    self.initial_tvec = tvec.copy()
                    self.initial_R, _ = cv2.Rodrigues(rvec)
                    self.reset_position = False

                # Compute rotation matrices
                R_current, _ = cv2.Rodrigues(rvec)

                # Translation relative to initial camera frame (still metric)
                relative_tvec_camera = tvec - self.initial_tvec

                # Rotate translation into the initial head frame
                relative_tvec_head = self.initial_R.T @ (
                    R_current @ relative_tvec_camera
                )

                y, z, x = relative_tvec_head.flatten()
                y = -y

                tmp_position = Position(x, y, z)

        return {"position": tmp_position, "orientation": tmp_orientation}
