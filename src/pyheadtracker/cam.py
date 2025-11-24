"""
Access position and orientation data via webcam-based head tracking

Classes
- `MPFaceLandmarker`: Webcam-based head tracker using OpenCV and MediaPipe Face Landmarker
"""

from importlib import resources
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from .dtypes import Quaternion, YPR, Position, HTBase
from .utils import ypr2quat


class MPFaceLandmarker(HTBase):
    """Webcam-based head tracker using OpenCV and MediaPipe Face Landmarker

    This class uses MediaPipe's Face Landmarker [1] to track head position and orientation using a (web-)cam. A mesh of 478 face landmarks is fitted to the detected face, from which 6 key points are used to estimate head pose via solvePnP. Orientation is derived from MediaPipe's facial transformation matrix. Tracking of the position is still experimental and might be inaccurate. Parts of the computation are offloaded to the GPU if available. By default, the built-in MediaPipe Face Landmarker model is used, but custom model weights can be provided. The supplied model weights (09/15/2022) are licensed under the Apache 2.0 license.

    Attributes
    ----------
    cam_index : int
        The index of the webcam to use.
    landmark_points_idx : list[int], optional
        Indices of the facial landmarks to use for pose estimation.
    landmark_points_3d : np.ndarray, optional
        Corresponding 3D model points for the selected landmarks. Note, that mediapipe's coordinate system is used (right-handed, x: right, y: down, z: forward).
    orient_format : str
        The format for orientation data. Possible values are "q" (Quaternion) or "ypr" (Yaw, Pitch, Roll).
    reset_orientation : bool
        Flag to indicate whether to reset orientation zeroing on the next read.
    reset_position : bool
        Flag to indicate whether to reset position zeroing on the next read.
    is_opened : bool
        Indicates whether the camera is opened.
    __FaceLandmarkerOptions : vision.FaceLandmarkerOptions
        MediaPipe Face Landmarker options.
    __landmarker : vision.FaceLandmarker
        Internal MediaPipe Face Landmarker instance.
    __cap : cv2.VideoCapture
        Internal OpenCV VideoCapture instance.
    __frame_count : int
        Frame counter for MediaPipe processing.
    __frame_width : int
        Width of the video frames.
    __frame_height : int
        Height of the video frames.
    __camera_matrix : np.ndarray
        Camera intrinsic matrix.
    __dist_coeffs : np.ndarray
        Camera distortion coefficients.
    __initial_rotation_matrix : np.ndarray
        Initial rotation matrix for orientation zeroing.
    __initial_R : np.ndarray
        Initial rotation matrix for position zeroing.
    __initial_tvec : np.ndarray
        Initial translation vector for position zeroing.

    Methods
    -------
    open()
        Initializes the webcam and MediaPipe Face Landmarker.
    close()
        Releases the webcam and MediaPipe resources.
    list_available_cameras(max_index: int = 20) -> list[int]
        Lists all available camera indices on the system.
    zero()
        Use the current position and orientation as reference (zero) values.
    zero_orientation()
        Uses the current orientation as reference (zero) value.
    zero_position()
        Uses the current position as reference (zero) value.
    read_orientation() -> Quaternion or YPR or None
        Returns if available the current head orientation as a Quaternion or YPR object.
    read_position() -> Position or None
        Returns if available the current head position in meters as a Position object.
    read_pose() -> dict or None
        Returns if available the current head position and orientation as a dictionary with Position and Quaternion or YPR objects.

    References
    ----------
    [1] MediaPipe Face Landmarker: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker
    """

    def __init__(
        self,
        cam_index: int = 0,
        model_weights: Optional[str] = None,
        min_face_detection_confidence: float = 0.8,
        min_face_presence_confidence: float = 0.8,
        min_tracking_confidence: float = 0.8,
        landmark_points_idx: Optional[list[int]] = None,
        landmark_points_3d: Optional[np.ndarray] = None,
        orient_format: str = "q",
    ):
        """
        Parameters
        ----------
        cam_index : int
            The index of the webcam to use.
        model_weights : str, optional
            Path to custom model weights. If None, the default built-in model is used.
        min_face_detection_confidence : float, optional
            Minimum confidence value ([0.0, 1.0]) for face detection to be considered successful. Defaults to 0.8.
        min_face_presence_confidence : float, optional
            Minimum confidence value ([0.0, 1.0]) for the face presence to be considered detected successfully. Defaults to 0.8.
        min_tracking_confidence : float, optional
            Minimum confidence value ([0.0, 1.0]) for the face landmarks to be considered tracked successfully. Defaults to 0.8.
        landmark_points_idx : list[int], optional
            Indices of the facial landmarks to use for pose estimation.
        landmark_points_3d : np.ndarray, optional
            Corresponding 3D model points for the selected landmarks. Note, that mediapipe's coordinate system is used (right-handed, x: right, y: down, z: forward).
        orient_format : str
            The format for orientation data. Possible values are "q" (Quaternion) or "ypr" (Yaw, Pitch, Roll).
        """
        self.orient_format = orient_format
        self.cam_index = cam_index

        # Load default model weights if not provided
        if model_weights is None:
            try:
                # Use importlib.resources for deployed packages
                if hasattr(resources, "files"):
                    # Python 3.9+
                    data_path = resources.files("pyheadtracker").joinpath(
                        "data/mediapipe-facelandmarker/face_landmarker_v2_with_blendshapes.task"
                    )
                    model_weights = str(data_path)
                else:
                    # Fallback for older Python versions
                    model_weights = str(
                        Path(__file__).parent
                        / "data/mediapipe-facelandmarker/face_landmarker_v2_with_blendshapes.task"
                    )
            except Exception:
                # Final fallback to relative path
                model_weights = "data/mediapipe-facelandmarker/face_landmarker_v2_with_blendshapes.task"

        assert orient_format in [
            "q",
            "ypr",
        ], 'orient_format must be "q" (Quaternion) or "ypr" (Yaw, Pitch, Roll)'

        assert (
            min_face_detection_confidence >= 0.0
            and min_face_detection_confidence <= 1.0
        ), "min_face_detection_confidence must be in [0.0, 1.0]"
        assert (
            min_face_presence_confidence >= 0.0 and min_face_presence_confidence <= 1.0
        ), "min_face_presence_confidence must be in [0.0, 1.0]"
        assert (
            min_tracking_confidence >= 0.0 and min_tracking_confidence <= 1.0
        ), "min_tracking_confidence must be in [0.0, 1.0]"

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

        # Initialize MediaPipe Face Landmarker
        BaseOptions = python.BaseOptions(
            model_asset_path=model_weights,
        )
        self.__FaceLandmarkerOptions = vision.FaceLandmarkerOptions(
            base_options=BaseOptions,  # uses built-in model
            min_face_detection_confidence=min_face_detection_confidence,
            min_face_presence_confidence=min_face_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=True,
            num_faces=1,
            running_mode=vision.RunningMode.VIDEO,
        )

        # Internal variables
        self.__landmarker = None
        self.__cap = None
        self.__frame_count = 0
        self.__frame_width = 0
        self.__frame_height = 0

        self.__camera_matrix = None
        self.__dist_coeffs = None

        self.__initial_rotation_matrix = None
        self.__initial_R = None
        self.__initial_tvec = None

        self.reset_orientation = True
        self.reset_position = True

        self.is_opened = False

    def open(self):
        """Initializes the webcam and MediaPipe Face Landmarker."""

        self.__landmarker = vision.FaceLandmarker.create_from_options(
            self.__FaceLandmarkerOptions
        )

        self.__cap = cv2.VideoCapture(self.cam_index)

        # Double-check camera can actually read frames
        if not self.__cap.isOpened():
            raise RuntimeError(
                f"Failed to open camera with index {self.cam_index}. Use pyheadtracker.cam.list_available_cameras() to see available cameras."
            )

        self.__frame_count = 0

        self.__frame_width = int(self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.__frame_height = int(self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        focal_length = self.__frame_width

        self.__camera_matrix = np.array(
            [
                [focal_length, 0, self.__frame_width / 2],
                [0, focal_length, self.__frame_height / 2],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )

        self.__dist_coeffs = np.zeros((4, 1))

        self.is_opened = True

    @staticmethod
    def list_available_cameras(max_index: int = 20) -> list[int]:
        """
        List all available camera indices on the system.

        Parameters
        ----------
        max_index : int
            Maximum camera index to check (default 10).

        Returns
        -------
        list[int]
            List of available camera indices.
        """

        # Suppress OpenCV logging
        cv2.setLogLevel(0)

        available_cameras = []
        for i in range(max_index):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                if ret:
                    available_cameras.append(i)

        # Restore OpenCV logging level to default
        cv2.setLogLevel(1)

        return available_cameras

    def close(self):
        """Releases the webcam and MediaPipe resources."""
        if self.__cap is not None:
            self.__cap.release()
            self.__cap = None
            self.__landmarker = None
            self.is_opened = False
        cv2.destroyAllWindows()

    def read_orientation(self) -> YPR | Quaternion | None:
        """Returns if available the current head orientation as a Quaternion or YPR object.

        Returns
        -------
        Quaternion or YPR or None
            The current head orientation, or None if not available.
        """
        pose = self.__read_pose_internal(calculate_orientation=True)
        if pose is None or pose["orientation"] is None:
            return None
        orientation = pose["orientation"]
        if isinstance(orientation, (YPR, Quaternion)):
            return orientation
        return None

    def read_position(self) -> Position | None:
        """Returns if available the current head position as a Position object.

        Returns
        -------
        Position or None
            The current head position, or None if not available.
        """
        pose = self.__read_pose_internal(calculate_position=True)
        if pose is None or pose["position"] is None:
            return None
        position = pose["position"]
        return position if isinstance(position, Position) else None

    def read_pose(self) -> dict[str, Position | Quaternion | YPR | None] | None:
        """Returns if available the current head position and orientation as a dictionary with Position and Quaternion or YPR objects.

        Returns
        -------
        dict[str, Position | Quaternion | YPR] or None
            The current head position and orientation, or None if not available.
        """
        pose = self.__read_pose_internal(
            calculate_orientation=True, calculate_position=True
        )
        if pose is None:
            return None
        return pose

    def zero(self):
        """Use the current position and orientation as reference (zero) values."""
        self.reset_orientation = True
        self.reset_position = True

    def zero_orientation(self):
        """Uses the current orientation as reference (zero) value."""
        self.reset_orientation = True

    def zero_position(self):
        """Uses the current position as reference (zero) value."""
        self.reset_position = True

    def __read_pose_internal(
        self, calculate_orientation: bool = False, calculate_position: bool = False
    ) -> dict[str, Position | Quaternion | YPR | None] | None:
        """Internal method to calculate position and orientation

        Parameters
        ----------
        calculate_orientation : bool, optional
            Flag to calculate orientation, by default False
        calculate_position : bool, optional
            Flag to calculate position, by default False

        Returns
        -------
        dict[str, Position | Quaternion | YPR] or None
            The current head position and orientation, or None if not available.

        Raises
        ------
        RuntimeError
            If the camera is not opened when attempting to read orientation or position.
        """

        if not self.is_opened or self.__cap is None or self.__landmarker is None:
            raise RuntimeError(
                "Camera is not opened. Call 'open()' before reading orientation."
            )

        # Read frame from webcam
        ret, frame = self.__cap.read()
        if not ret:
            return None

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
        )

        # Process frame with MediaPipe Face Landmarker
        result = self.__landmarker.detect_for_video(mp_image, self.__frame_count)
        self.__frame_count += 1

        tmp_orientation = None
        tmp_position = None

        # Calculate orientation if requested
        if calculate_orientation and result.facial_transformation_matrixes:
            # Extract transformation matrix
            transformation_matrix = np.array(
                result.facial_transformation_matrixes[0].data
            ).reshape(4, 4)

            # Extract rotation matrix and translation vector
            rotation_matrix = transformation_matrix[:3, :3]

            # Initialize initial rotation matrix if needed or zeroed
            if self.__initial_rotation_matrix is None or self.reset_orientation:
                self.__initial_rotation_matrix = rotation_matrix.copy()
                self.reset_orientation = False

            # Calculate relative rotation matrix
            relative_rotation_matrix = (
                rotation_matrix @ self.__initial_rotation_matrix.T
            )

            # Convert rotation matrix to yaw, pitch, roll
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

            # Provide orientation in the requested format
            tmp_orientation = (
                YPR(yaw, pitch, roll)
                if self.orient_format == "ypr"
                else ypr2quat(YPR(yaw, pitch, roll))
            )

        # Calculate position if requested
        if calculate_position and result.face_landmarks:
            # Extract 2D image points
            face_landmarks = result.face_landmarks[0]
            image_points = np.array(
                [
                    [
                        face_landmarks[idx].x * self.__frame_width,
                        face_landmarks[idx].y * self.__frame_height,
                    ]
                    for idx in self.landmark_points_idx
                ],
                dtype=np.float64,
            )

            if self.__camera_matrix is None or self.__dist_coeffs is None:
                raise RuntimeError(
                    "Camera intrinsic parameters are not initialized. Call 'open()' before reading position."
                )

            # Solve PnP for absolute position in meters
            success, rvec, tvec = cv2.solvePnP(
                self.landmark_points_3d,
                image_points,
                self.__camera_matrix,
                self.__dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE,
            )

            # Calculate relative position if successful
            if success:

                # Initialize initial position if needed or zeroed
                if (
                    self.__initial_R is None
                    or self.__initial_tvec is None
                    or self.reset_position
                ):
                    self.__initial_tvec = tvec.copy()
                    self.__initial_R, _ = cv2.Rodrigues(rvec)
                    self.reset_position = False

                # Compute rotation matrices
                R_current, _ = cv2.Rodrigues(rvec)

                # Translation relative to initial camera frame (still metric)
                relative_tvec_camera = tvec - self.__initial_tvec

                # Rotate translation into the initial head frame
                relative_tvec_head = self.__initial_R.T @ (
                    R_current @ relative_tvec_camera
                )

                # Convert to Position object (invert y to match right-handed coordinate system)
                y, z, x = relative_tvec_head.flatten()
                y = -y

                tmp_position = Position(x, y, z)

        return {"position": tmp_position, "orientation": tmp_orientation}
