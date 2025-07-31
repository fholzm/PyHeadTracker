import numpy as np


class Quaternion:
    """
    Represents a quaternion for 3D rotations.

    Attributes
    ----------
    w : float
        The scalar part of the quaternion.
    x : float
        The x component of the quaternion.
    y : float
        The y component of the quaternion.
    z : float
        The z component of the quaternion.

    Methods
    -------
    to_array() -> np.ndarray
        Converts the quaternion to a NumPy array [w, x, y, z].
    from_array(arr: np.ndarray) -> Quaternion
        Creates a quaternion from a NumPy array [w, x, y, z].
    __iter__() -> Iterator[float]
        Makes the Quaternion iterable.
    __getitem__(index: int) -> float
        Gets the quaternion component by index (w,x,y,z).
    __mul__(other: Quaternion) -> Quaternion
        Multiplies this quaternion by another quaternion (Hamilton product).
    __add__(other: Quaternion) -> Quaternion
        Adds this quaternion to another quaternion.
    conjugate() -> Quaternion
        Returns the conjugate of the quaternion.
    norm() -> float
        Computes the norm (magnitude) of the quaternion.
    normalize() -> Quaternion
        Normalizes the quaternion to have a unit norm.
    inverse() -> Quaternion
        Computes the inverse of the quaternion.
    """

    def __init__(self, w, x, y, z):
        """
        Parameters
        ----------
        w : float
            The scalar part of the quaternion.
        x : float
            The x component of the quaternion.
        y : float
            The y component of the quaternion.
        z : float
            The z component of the quaternion.
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

        Returns
        -------
        np.ndarray
            A NumPy array containing the quaternion components [w, x, y, z].
        """
        return np.array([self.w, self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr):
        """
        Create a quaternion from a NumPy array [w, x, y, z].

        Parameters
        ----------
        arr : np.ndarray, list, or tuple
            A NumPy array, list, or tuple containing the quaternion components [w, x, y, z].
        """
        if len(arr) != 4:
            raise ValueError("Array must have exactly 4 elements.")
        return cls(arr[0], arr[1], arr[2], arr[3])

    def __iter__(self):
        """
        Make the Quaternion iterable.
        """
        return iter(self.to_array())

    def __getitem__(self, index: int):
        """
        Get the quaternion component by index (w,x,y,z).
        """
        if index < 0 or index > 3:
            raise IndexError("Index must be 0, 1, 2, or 3 for w, x, y, z respectively.")
        return self.to_array()[index]

    def __mul__(self, other):
        """
        Quaternion multiplication (Hamilton product).

        Parameters
        ----------
        other : Quaternion
            The quaternion to multiply with.

        Returns
        -------
        Quaternion
            The result of the Hamilton product of this quaternion and the other quaternion.
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

        Parameters
        ----------
        other : Quaternion
            The quaternion to add to this quaternion.

        Returns
        -------
        Quaternion
            The result of the addition of this quaternion and the other quaternion.
        """
        if not isinstance(other, Quaternion):
            raise TypeError("Addition is only supported between two quaternions.")

        return Quaternion(
            self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z
        )

    def conjugate(self):
        """
        Return the conjugate of the quaternion.
        The conjugate of a quaternion is obtained by negating the vector part (x, y, z).

        Returns
        -------
        Quaternion
            The conjugate of the quaternion.
        """
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def norm(self):
        """
        Compute the norm (magnitude) of the quaternion.

        Returns
        -------
        float
            The norm of the quaternion, which is the square root of the sum of the squares of its components.
        """
        return np.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        """
        Normalize the quaternion to have a unit norm.

        Returns
        -------
        Quaternion
            A new quaternion with a unit norm.
        """
        norm = self.norm()
        if norm == 0:
            raise ZeroDivisionError("Cannot normalize a quaternion with zero norm.")
        return Quaternion(self.w / norm, self.x / norm, self.y / norm, self.z / norm)

    def inverse(self):
        """
        Compute the inverse of the quaternion.

        The inverse of a quaternion is its conjugate divided by the square of its norm.

        Returns
        -------
        Quaternion
            The inverse of the quaternion.
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


class YPR:
    """
    Represents Yaw, Pitch, Roll angles in radians.

    Attributes
    ----------
    yaw : float
        The yaw angle in radians.
    pitch : float
        The pitch angle in radians.
    roll : float
        The roll angle in radians.
    sequence : str
        The sequence of rotations, either "ypr" (Yaw-Pitch-Roll) or "rpy" (Roll-Pitch-Yaw).

    Methods
    -------
    to_array() -> np.ndarray
        Converts the YPR object to a NumPy array.
    from_array(arr: np.ndarray, sequence: str = "ypr") -> YPR
        Creates a YPR object from a NumPy array.
    __iter__() -> Iterator[float]
        Returns an iterator over the YPR angles.
    __getitem__(index: int) -> float
        Gets the YPR component by index (0 for yaw, 1 for pitch, 2 for roll).
    __add__(other: YPR) -> YPR
        Adds another YPR to this YPR.
    __sub__(other: YPR) -> YPR
        Subtracts another YPR from this YPR.
    __wrap_angles(y: float, p: float, r: float) -> Tuple[float, float, float]
        Wraps angles to the range [-pi, pi] radians.
    to_degrees() -> np.ndarray
        Converts the YPR angles to degrees.
    """

    def __init__(self, yaw, pitch, roll, sequence: str = "ypr"):
        """
        Parameters
        ----------
        yaw : float
            The yaw angle in radians.
        pitch : float
            The pitch angle in radians.
        roll : float
            The roll angle in radians.
        """
        assert sequence in ["ypr", "rpy"], "Sequence must be 'ypr' or 'rpy'"
        assert (
            np.abs(yaw) < 2 * np.pi
            or np.abs(pitch) < 2 * np.pi
            or np.abs(roll) < 2 * np.pi
        ), "Angles must be in radians and should be in the range [-pi, pi]."

        yaw, pitch, roll = self.__wrap_angles(yaw, pitch, roll)

        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.sequence = sequence

    def __repr__(self):
        """
        String representation of the YPR angles.
        """
        return f"YPR(yaw={self.yaw}, pitch={self.pitch}, roll={self.roll}, sequence={self.sequence})"

    def to_array(self):
        """
        Convert Yaw, Pitch, Roll to a NumPy array.

        Returns
        -------
        np.ndarray
            A NumPy array containing the Yaw, Pitch, Roll angles in radians.
        """
        return np.array([self.yaw, self.pitch, self.roll])

    @classmethod
    def from_array(cls, arr, sequence: str = "ypr"):
        """
        Create YPR from a NumPy array.

        Parameters
        ----------
        arr : np.ndarray, list, or tuple
            A NumPy array, list, or tuple containing the Yaw, Pitch, Roll angles in radians.
        """
        if len(arr) != 3:
            raise ValueError("Array must have exactly 3 elements.")
        return cls(arr[0], arr[1], arr[2], sequence=sequence)

    def __iter__(self):
        """
        Make the YPR iterable.

        Returns
        -------
        Iterator[float]
            An iterator over the Yaw, Pitch, Roll angles in radians.
        """
        return iter(self.to_array())

    def __getitem__(self, index: int):
        """
        Get the YPR component by index.

        Parameters
        ----------
        index : int
            The index of the component to retrieve (0 for yaw, 1 for pitch, 2 for roll).

        Returns
        -------
        float
            The Yaw, Pitch, or Roll angle in radians.
        """
        if index < 0 or index > 2:
            raise IndexError(
                "Index must be 0, 1, or 2 for yaw, pitch, roll respectively."
            )
        return self.to_array()[index]

    def __add__(self, other):
        """
        Add another YPR to this YPR.

        Parameters
        ----------
        other : YPR
            The YPR to add to this YPR.
        Returns
        -------
        YPR
            The result of the addition of this YPR and the other YPR.
        """
        if not isinstance(other, YPR):
            raise TypeError("Addition is only supported between two YPRs.")
        if self.sequence != other.sequence:
            raise ValueError("Cannot add YPRs with different angle sequences.")

        y = self.yaw + other.yaw
        p = self.pitch + other.pitch
        r = self.roll + other.roll

        y, p, r = self.__wrap_angles(y, p, r)

        return YPR(
            y,
            p,
            r,
            sequence=self.sequence,
        )

    def __sub__(self, other):
        """
        Subtract another YPR from this YPR.

        Parameters
        ----------
        other : YPR
            The YPR to subtract from this YPR.

        Returns
        -------
        YPR
            The result of the subtraction of this YPR and the other YPR.
        """
        if not isinstance(other, YPR):
            raise TypeError("Subtraction is only supported between two YPRs.")
        if self.sequence != other.sequence:
            raise ValueError("Cannot subtract YPRs with different angle sequences.")

        y = self.yaw - other.yaw
        p = self.pitch - other.pitch
        r = self.roll - other.roll

        y, p, r = self.__wrap_angles(y, p, r)

        return YPR(
            y,
            p,
            r,
            sequence=self.sequence,
        )

    def __wrap_angles(self, y, p, r):
        """
        Wrap angles to the range [-pi, pi] radians.

        Parameters
        ----------
        y : float
            The yaw angle in radians.
        p : float
            The pitch angle in radians.
        r : float
            The roll angle in radians.

        Returns
        -------
        Tuple[float, float, float]
            The wrapped angles in radians.
        """
        y = (y + np.pi) % (2 * np.pi) - np.pi
        p = (p + np.pi) % (2 * np.pi) - np.pi
        r = (r + np.pi) % (2 * np.pi) - np.pi

        return y, p, r

    def to_degrees(self):
        """
        Convert the Yaw, Pitch, Roll angles to degrees.

        Returns
        -------
        ndarray
            The Yaw, Pitch, Roll angles in degrees.
        """
        return np.degrees(self.to_array())


class Position:
    """
    Represents a 3D position in space as Cartesian coordinates.

    Attributes
    ----------
    x : float
        The x coordinate of the position.
    y : float
        The y coordinate of the position.
    z : float
        The z coordinate of the position.

    Methods
    -------
    to_array() -> np.ndarray
        Converts the position to a NumPy array [x, y, z].
    from_array(arr: np.ndarray) -> Position
        Creates a position from a NumPy array [x, y, z].
    __iter__() -> Iterator[float]
        Makes the Position iterable.
    __getitem__(index: int) -> float
        Gets the position component by index (0 for x, 1 for y, 2 for z).
    __mul__(factor: float or np.ndarray) -> Position
        Scales the position by a factor or a NumPy array.
    __add__(other: Position) -> Position
        Adds another position to this position.
    __sub__(other: Position) -> Position
        Subtracts another position from this position.
    distance_to(other: Position) -> float
        Calculates the Euclidean distance to another position.
    """

    def __init__(self, x, y, z):
        """
        Parameters
        ----------
        x : float
            The x coordinate of the position.
        y : float
            The y coordinate of the position.
        z : float
            The z coordinate of the position.
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

        Returns
        -------
        np.ndarray
            A NumPy array containing the position coordinates [x, y, z].
        """
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr):
        """
        Create a position from a NumPy array, list, or tuple [x, y, z].

        Parameters
        ----------
        arr : np.ndarray, list, or tuple
            A NumPy array, list, or tuple containing the position coordinates [x, y, z].
        """
        if len(arr) != 3:
            raise ValueError("Array must have exactly 3 elements.")
        return cls(arr[0], arr[1], arr[2])

    def __iter__(self):
        """
        Make the Position iterable.
        """
        return iter(self.to_array())

    def __getitem__(self, index: int):
        """
        Get the position component by index.

        Parameters
        ----------
        index : int
            The index of the position component to retrieve (0 for x, 1 for y, 2 for z).

        Returns
        -------
        float
            The x, y, or z coordinate of the position.
        """
        if index < 0 or index > 2:
            raise IndexError("Index must be 0, 1, or 2 for x, y, z respectively.")
        return self.to_array()[index]

    def __mul__(self, factor):
        """
        Scale the position by a factor. Either a scalar, applied to all dimensions, or a NumPy array with 3 elements for individual scaling for each dimension.

        Parameters
        ----------
        factor : float, np.ndarray, list, or tuple
            A scalar to scale all dimensions or a NumPy array with 3 elements to scale each dimension individually.

        Returns
        -------
        Position
            A new Position object with scaled coordinates.
        """
        if not isinstance(factor, (int, float, np.ndarray, list, tuple)):
            raise TypeError("Factor must be a scalar or a NumPy array.")

        if isinstance(factor, (np.ndarray, list, tuple)) and len(factor) != 3:
            raise ValueError("NumPy array factor must have exactly 3 elements.")

        if isinstance(factor, (np.ndarray, list, tuple)):
            return Position(self.x * factor[0], self.y * factor[1], self.z * factor[2])
        else:
            return Position(self.x * factor, self.y * factor, self.z * factor)

    def __add__(self, other):
        """
        Add another position to this position.

        Parameters
        ----------
        other : Position
            The position to add to this position.

        Returns
        -------
        Position
            A new Position object representing the sum of the two positions.
        """
        if not isinstance(other, Position):
            raise TypeError("Addition is only supported between two positions.")

        return Position(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """
        Subtract another position from this position.

        Parameters
        ----------
        other : Position
            The position to subtract from this position.

        Returns
        -------
        Position
            A new Position object representing the difference between the two positions.
        """
        if not isinstance(other, Position):
            raise TypeError("Subtraction is only supported between two positions.")

        return Position(self.x - other.x, self.y - other.y, self.z - other.z)

    def distance_to(self, other):
        """
        Calculate the Euclidean distance to another position.

        Parameters
        ----------
        other : Position
            The position to which the distance is calculated.

        Returns
        -------
        float
            The Euclidean distance between this position and the other position.
        """
        if not isinstance(other, Position):
            raise TypeError(
                "Distance calculation is only supported between two positions."
            )

        return np.sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )
