import numpy as np
from typing import Optional
from .utils import ypr2quat, quat2ypr


class Quaternion:
    def __init__(self, w, x, y, z):
        """
        Initialize a quaternion with components w, x, y, z.
        """
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        """
        String representation of the quaternion.
        """
        return f"Quaternion(w={self.w}, x={self.x}, y={self.y}, z={self.z})"

    def to_array(self):
        """
        Convert the quaternion to a NumPy array [w, x, y, z].
        """
        return np.array([self.w, self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr):
        """
        Create a quaternion from a NumPy array [w, x, y, z].
        """
        if len(arr) != 4:
            raise ValueError("Array must have exactly 4 elements.")
        return cls(arr[0], arr[1], arr[2], arr[3])

    def __iter__(self):
        """
        Make the Quaternion iterable.
        """
        return iter(self.to_array())

    def __mul__(self, other):
        """
        Quaternion multiplication (Hamilton product).
        """
        if not isinstance(other, Quaternion):
            raise TypeError("Multiplication is only supported between two quaternions.")

        # Hamilton product formula
        w1, x1, y1, z1 = self.w, self.x, self.y, self.z
        w2, x2, y2, z2 = other.w, other.x, other.y, other.z

        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

        return Quaternion(w, x, y, z)

    def __add__(self, other):
        """
        Quaternion addition.
        """
        if not isinstance(other, Quaternion):
            raise TypeError("Addition is only supported between two quaternions.")

        return Quaternion(
            self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z
        )

    def conjugate(self):
        """
        Return the conjugate of the quaternion.
        """
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def norm(self):
        """
        Compute the norm (magnitude) of the quaternion.
        """
        return np.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        """
        Normalize the quaternion to have a unit norm.
        """
        norm = self.norm()
        if norm == 0:
            raise ZeroDivisionError("Cannot normalize a quaternion with zero norm.")
        return Quaternion(self.w / norm, self.x / norm, self.y / norm, self.z / norm)

    def inverse(self):
        """
        Compute the inverse of the quaternion.
        """
        norm_squared = self.norm() ** 2
        if norm_squared == 0:
            raise ZeroDivisionError("Cannot invert a quaternion with zero norm.")
        conjugate = self.conjugate()
        return Quaternion(
            conjugate.w / norm_squared,
            conjugate.x / norm_squared,
            conjugate.y / norm_squared,
            conjugate.z / norm_squared,
        )

    def to_ypr(self, degrees: bool = False, sequence: str = "ypr"):
        """
        Convert the quaternion to Yaw, Pitch, Roll angles.
        """
        return quat2ypr(self, degrees=degrees, sequence=sequence)


class YPR:
    def __init__(self, yaw, pitch, roll, degrees: bool = False, sequence: str = "ypr"):
        """
        Initialize Yaw, Pitch, Roll angles.
        """
        assert sequence in ["ypr", "rpy"], "Sequence must be 'ypr' or 'rpy'"

        yaw, pitch, roll = self._wrap_angles(yaw, pitch, roll, degrees)

        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.sequence = sequence
        self.degrees = degrees

    def __repr__(self):
        """

        String representation of the YPR angles.
        """
        return f"YPR(yaw={self.yaw}, pitch={self.pitch}, roll={self.roll}, degrees={self.degrees}, sequence={self.sequence})"

    def to_array(self):
        """
        Convert Yaw, Pitch, Roll to a NumPy array.
        """
        return np.array([self.yaw, self.pitch, self.roll])

    @classmethod
    def from_array(cls, arr, degrees: bool = False, sequence: str = "ypr"):
        """
        Create YPR from a NumPy array.
        """
        if len(arr) != 3:
            raise ValueError("Array must have exactly 3 elements.")
        return cls(arr[0], arr[1], arr[2], degrees=degrees, sequence=sequence)

    def __iter__(self):
        """
        Make the YPR iterable.
        """
        return iter(self.to_array())

    def __add__(self, other):
        """
        Add another YPR to this YPR.
        """
        if not isinstance(other, YPR):
            raise TypeError("Addition is only supported between two YPRs.")
        if self.sequence != other.sequence:
            raise ValueError("Cannot add YPRs with different angle sequences.")
        if self.degrees != other.degrees:
            raise ValueError("Cannot add YPRs with different degree settings.")

        y = self.yaw + other.yaw
        p = self.pitch + other.pitch
        r = self.roll + other.roll

        y, p, r = self._wrap_angles(y, p, r, degrees=self.degrees)

        return YPR(
            y,
            p,
            r,
            degrees=self.degrees,
            sequence=self.sequence,
        )

    def __sub__(self, other):
        """
        Subtract another YPR from this YPR.
        """
        if not isinstance(other, YPR):
            raise TypeError("Subtraction is only supported between two YPRs.")
        if self.sequence != other.sequence:
            raise ValueError("Cannot subtract YPRs with different angle sequences.")
        if self.degrees != other.degrees:
            raise ValueError("Cannot subtract YPRs with different degree settings.")

        y = self.yaw - other.yaw
        p = self.pitch - other.pitch
        r = self.roll - other.roll

        y, p, r = self._wrap_angles(y, p, r, degrees=self.degrees)

        return YPR(
            y,
            p,
            r,
            degrees=self.degrees,
            sequence=self.sequence,
        )

    def _wrap_angles(self, y, p, r, degrees: Optional[bool] = None):
        """
        Wrap angles to the range [-180, 180] degrees or [-pi, pi] radians.
        """
        if degrees is None:
            degrees = self.degrees

        if degrees:
            y = (y + 180) % 360 - 180
            p = (p + 180) % 360 - 180
            r = (r + 180) % 360 - 180
        else:
            y = (y + np.pi) % (2 * np.pi) - np.pi
            p = (p + np.pi) % (2 * np.pi) - np.pi
            r = (r + np.pi) % (2 * np.pi) - np.pi

        return y, p, r

    def to_quaternion(self):
        """
        Convert Yaw, Pitch, Roll to a Quaternion.
        """
        return ypr2quat(self.to_array(), degrees=self.degrees, sequence=self.sequence)


class Position:
    def __init__(self, x, y, z):
        """
        Initialize a position with coordinates x, y, z.
        """
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        """
        String representation of the position.
        """
        return f"Position(x={self.x}, y={self.y}, z={self.z})"

    def to_array(self):
        """
        Convert the position to a NumPy array [x, y, z].
        """
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr):
        """
        Create a position from a NumPy array [x, y, z].
        """
        if len(arr) != 3:
            raise ValueError("Array must have exactly 3 elements.")
        return cls(arr[0], arr[1], arr[2])

    def __iter__(self):
        """
        Make the Position iterable.
        """
        return iter(self.to_array())

    def __mul__(self, factor):
        """
        Scale the position by a factor.
        """
        if not isinstance(factor, (int, float)) and not isinstance(factor, np.ndarray):
            raise TypeError("Factor must be a scalar or a NumPy array.")

        if isinstance(factor, np.ndarray) and len(factor) != 3:
            raise ValueError("NumPy array factor must have exactly 3 elements.")

        if isinstance(factor, np.ndarray):
            return Position(self.x * factor[0], self.y * factor[1], self.z * factor[2])
        else:
            return Position(self.x * factor, self.y * factor, self.z * factor)

    def __add__(self, other):
        """
        Add another position to this position.
        """
        if not isinstance(other, Position):
            raise TypeError("Addition is only supported between two positions.")

        return Position(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """
        Subtract another position from this position.
        """
        if not isinstance(other, Position):
            raise TypeError("Subtraction is only supported between two positions.")

        return Position(self.x - other.x, self.y - other.y, self.z - other.z)

    def distance_to(self, other):
        """
        Calculate the Euclidean distance to another position.
        """
        if not isinstance(other, Position):
            raise TypeError(
                "Distance calculation is only supported between two positions."
            )

        return np.sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )
