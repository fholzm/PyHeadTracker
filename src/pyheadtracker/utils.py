import numpy as np
from .dtypes import Quaternion, YPR


def quat2ypr(quat: Quaternion, sequence: str = "ypr"):
    """
    Convert a quaternion to yaw, pitch, and roll angles.
    :param quat: A numpy array or list with quaternion values [w, x, y, z].
    :return: A tuple (yaw, pitch, roll) in radians.
    """
    assert sequence in ["ypr", "rpy"], "Sequence must be 'ypr' or 'rpy'"

    e = 1 if sequence == "ypr" else -1

    qw, qx, xy, qz = quat

    pitch = np.arcsin(2 * (qw * xy + e * qz * qx))

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
    Convert yaw, pitch, and roll angles to a quaternion.
    :param yaw: Yaw angle in radians.
    :param pitch: Pitch angle in radians.
    :param roll: Roll angle in radians.
    :return: A numpy array with quaternion values [w, x, y, z].
    """
    assert ypr.sequence in ["ypr", "rpy"], "Sequence must be 'ypr' or 'rpy'"

    wa = np.cos(ypr[0] * 0.5)
    za = np.sin(ypr[0] * 0.5)
    wb = np.cos(ypr[1] * 0.5)
    yb = np.sin(ypr[1] * 0.5)
    wc = np.cos(ypr[2] * 0.5)
    xc = np.sin(ypr[2] * 0.5)

    if ypr.sequence == "ypr":
        qw = wc * wb * wa - xc * yb * za
        qx = wc * yb * za + xc * wb * wa
        qy = wc * yb * wa - xc * wb * za
        qz = wc * wb * za + xc * yb * wa
    else:  # sequence == "rpy"
        qw = wa * wb * wc - za * yb * xc
        qx = za * wb * wc + wa * yb * xc
        qy = wa * yb * wc - za * wb * xc
        qz = wa * wb * xc + za * yb * wc

    return np.array([qw, qx, qy, qz])
