"""
Utility functions for quaternion and YPR conversions, and angle unit conversions.

This module provides functions to convert between quaternions and YPR (Yaw, Pitch, Roll) angles,
as well as to convert angles between radians and degrees. It also includes type checking for input data.
It is part of the pyheadtracker package, which provides tools for head tracking and orientation data.

Functions:
- `quat2ypr(quat, sequence)`: Converts a quaternion to YPR angles.
- `ypr2quat(ypr)`: Converts YPR angles to a quaternion.
- `rad2deg(input_data)`: Converts radians to degrees.
- `deg2rad(input_data)`: Converts degrees to radians.
"""

import numpy as np
from .dtypes import Quaternion, YPR


def quat2ypr(quat: Quaternion, sequence: str = "ypr", extrinsic: bool = False) -> YPR:
    """
    Convert a Quaternion to an YPR (yaw, pitch, roll) object.

    Parameters
    ----------
    quat : Quaternion
        The quaternions object to be converted.
    sequence : str, optional
        The sequence of angles, either "ypr" (Yaw, Pitch, Roll) or "rpy" (Roll, Pitch, Yaw).
        Default is "ypr".
    extrinsic : bool, optional
        If True, use extrinsic rotations (rotations about the fixed axes). If False, use intrinsic rotations (rotations about the moving axes).
        Default is False.

    Returns
    -------
    YPR
        An YPR object containing the converted angles in radians.

    References
    ----------
    [1] E. Bernardes, “OrigaBot: Origami-based Reconfigurable Robots for Multi-modal Locomotion,” phdthesis, Aix-Marseille University, 2023. Accessed: Oct. 10, 2025. [Online]. Available: https://theses.hal.science/tel-04646218
    """
    assert sequence in ["ypr", "rpy"], "Sequence must be 'ypr' or 'rpy'"

    if extrinsic:
        sequence = sequence[::-1]  # Reverse for intrinsic rotations

    if sequence == "ypr":
        i = int(3)
        j = int(2)
        k = int(1)
    elif sequence == "rpy":
        i = int(1)
        j = int(2)
        k = int(3)
    else:
        raise ValueError("Sequence must be 'ypr' or 'rpy'")

    e = int((-i + j) * (-j + k) * (-k + i) / 2)

    a = quat[0] - quat[j]
    b = quat[i] + quat[k] * e
    c = quat[j] + quat[0]
    d = quat[k] * e - quat[i]

    theta2 = 2 * np.atan2(np.sqrt(c**2 + d**2), np.sqrt(a**2 + b**2))
    theta_plus = np.atan2(b, a)
    theta_minus = np.atan2(d, c)

    if np.abs(theta2) < 1e-6:
        theta1 = 0
        theta3 = 2 * theta_plus
    elif np.abs(theta2 - np.pi) < 1e-6:
        theta1 = 0
        theta3 = 2 * theta_minus
    else:
        theta1 = theta_plus - theta_minus
        theta3 = theta_plus + theta_minus

    theta3 *= e
    theta2 -= np.pi / 2

    # Wrap angles to the range [-pi, pi]
    theta1 = np.atan2(np.sin(theta1), np.cos(theta1))
    theta2 = np.atan2(np.sin(theta2), np.cos(theta2))
    theta3 = np.atan2(np.sin(theta3), np.cos(theta3))

    return YPR(theta1, theta2, theta3, sequence)


def ypr2quat(ypr: YPR):
    """
    Converts a YPR to a Quaternion object.

    Parameters
    ----------
    ypr : YPR
        The YPR object to be converted.

    Returns
    -------
    Quaternion
        A Quaternion object containing the converted values.
    """
    assert ypr.sequence in ["ypr", "rpy"], "Sequence must be 'ypr' or 'rpy'"

    t0 = np.cos(ypr[0] * 0.5)
    t1 = np.sin(ypr[0] * 0.5)
    t2 = np.cos(ypr[2] * 0.5)
    t3 = np.sin(ypr[2] * 0.5)
    t4 = np.cos(ypr[1] * 0.5)
    t5 = np.sin(ypr[1] * 0.5)

    if ypr.sequence == "ypr":
        qw = t0 * t2 * t4 + t1 * t3 * t5
        qx = t0 * t3 * t4 - t1 * t2 * t5
        qy = t0 * t2 * t5 + t1 * t3 * t4
        qz = t1 * t2 * t4 - t0 * t3 * t5

    else:  # sequence == "rpy"
        qw = t0 * t2 * t4 - t1 * t3 * t5
        qx = t1 * t2 * t4 + t0 * t3 * t5
        qy = t0 * t3 * t4 - t1 * t2 * t5
        qz = t0 * t2 * t5 + t1 * t3 * t4

    return Quaternion(qw, qx, qy, qz)


def rad2deg(input_data):
    """
    Converts input data from radians to degrees.

    Parameters
    ----------
    input_data : float, list, np.ndarray, or YPR
        Input in radians.

    Returns
    -------
    float, list, np.ndarray, or YPR
        Converted data in degrees, with the same type as the input.
    """
    if isinstance(input_data, (float, int)):  # Single float or int
        return np.degrees(input_data)
    elif isinstance(input_data, list):  # List of values
        return [np.degrees(x) for x in input_data]
    elif isinstance(input_data, np.ndarray):  # NumPy array
        return np.degrees(input_data)
    elif isinstance(input_data, YPR):  # Custom YPR object
        return input_data.to_degrees()
    else:
        raise TypeError(
            "Unsupported input type. Supported types: float, list, np.ndarray, YPR."
        )


def deg2rad(input_data):
    """
    Converts input data from degrees to radians.

    Parameters
    ----------
    input_data : float, list, or np.ndarray
        Input in degrees.

    Returns
    -------
    float, list, or np.ndarray
        Converted data in radians, with the same type as the input.
    """
    if isinstance(input_data, (float, int)):  # Single float or int
        return np.radians(input_data)
    elif isinstance(input_data, list):  # List of values
        return [np.radians(x) for x in input_data]
    elif isinstance(input_data, np.ndarray):  # NumPy array
        return np.radians(input_data)
    else:
        raise TypeError(
            "Unsupported input type. Supported types: float, list, np.ndarray, YPR."
        )
