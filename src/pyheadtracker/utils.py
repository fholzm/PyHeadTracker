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


def quat2ypr(quat: Quaternion, sequence: str = "ypr"):
    """
    Convert a Quaternion to an YPR (yaw, pitch, roll) object.

    Parameters
    ----------
    quat : Quaternion
        The quaternions object to be converted.
    sequence : str, optional
        The sequence of angles, either "ypr" (Yaw, Pitch, Roll) or "rpy" (Roll, Pitch, Yaw).
        Default is "ypr".

    Returns
    -------
    YPR
        An YPR object containing the converted angles in radians.
    """
    assert sequence in ["ypr", "rpy"], "Sequence must be 'ypr' or 'rpy'"

    e = -1 if sequence == "ypr" else 1

    qw, qx, xy, qz = quat

    t0 = np.clip(2 * (qw * xy + e * qz * qx), -1.0, 1.0)
    pitch = np.arcsin(t0)

    if np.abs(pitch == np.pi):
        roll = 0
        yaw = np.arctan(qz, qw)
    else:
        t0 = 2.0 * (qw * qz - e * xy * qx)
        t1 = 1.0 - 2.0 * (qz * qz + xy * xy)

        yaw = np.arctan2(t0, t1)

        t0 = 2.0 * (qw * qx - e * qz * xy)
        t1 = 1.0 - 2.0 * (xy * xy + qx * qx)
        roll = np.arctan2(t0, t1)

    return YPR(yaw, pitch, roll, sequence)


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
