import pytest
import numpy as np
from pyheadtracker.dtypes import Quaternion, YPR
import pyheadtracker.utils

tolerance = 1e-2

quat_test = [
    Quaternion(1, 0, 0, 0),
    Quaternion(0, 1, 0, 0),
    Quaternion(0, 0, 1, 0),
    Quaternion(0, 0, 0, 1),
    Quaternion(0.7071, 0.7071, 0, 0),
    Quaternion(0.7071, 0, 0.7071, 0),
    Quaternion(0.7071, 0, 0, 0.7071),
    Quaternion(0.5, 0.5, 0.5, 0.5),
]

# TODO: Check sequence of ypr angles
ypr_test = [
    YPR(0, 0, 0, sequence="ypr"),
    YPR(0, 0, np.pi, sequence="ypr"),
    YPR(np.pi, 0, np.pi, sequence="ypr"),
    YPR(np.pi, 0, 0, sequence="ypr"),
    YPR(0, 0, np.pi / 2, sequence="ypr"),
    YPR(0, np.pi / 2, 0, sequence="ypr"),
    YPR(np.pi / 2, 0, 0, sequence="ypr"),
    YPR(np.pi / 2, 0, np.pi / 2, sequence="ypr"),
]


@pytest.mark.parametrize(
    "quat, ypr",
    list(zip(quat_test, ypr_test)),
)
def test_quat2ypr(quat, ypr):
    ypr_converted = pyheadtracker.utils.quat2ypr(quat)

    # Assert that the result is close to the expected value
    assert pytest.approx(ypr[0], abs=tolerance) == ypr_converted[0]
    assert pytest.approx(ypr[1], abs=tolerance) == ypr_converted[1]
    assert pytest.approx(ypr[2], abs=tolerance) == ypr_converted[2]


@pytest.mark.parametrize(
    "quat, ypr",
    list(zip(quat_test, ypr_test)),
)
def test_ypr2quat(quat, ypr):
    quat_converted = pyheadtracker.utils.ypr2quat(ypr)

    # Wrap values close to 1 or -1 to avoid issues with sign ambiguity
    qw_ref = np.abs(quat.w) if np.abs(quat.w) - 1 < tolerance else quat.w
    qx_ref = np.abs(quat.x) if np.abs(quat.x) - 1 < tolerance else quat.x
    qy_ref = np.abs(quat.y) if np.abs(quat.y) - 1 < tolerance else quat.y
    qz_ref = np.abs(quat.z) if np.abs(quat.z) - 1 < tolerance else quat.z

    qw_conv = (
        np.abs(quat_converted.w)
        if np.abs(quat_converted.w) - 1 < tolerance
        else quat_converted.w
    )
    qx_conv = (
        np.abs(quat_converted.x)
        if np.abs(quat_converted.x) - 1 < tolerance
        else quat_converted.x
    )
    qy_conv = (
        np.abs(quat_converted.y)
        if np.abs(quat_converted.y) - 1 < tolerance
        else quat_converted.y
    )
    qz_conv = np.abs(quat.z) if np.abs(quat.z) - 1 < tolerance else quat.z

    # Assert that the result is close to the expected value
    assert pytest.approx(qw_ref, abs=tolerance) == qw_conv
    assert pytest.approx(qx_ref, abs=tolerance) == qx_conv
    assert pytest.approx(qy_ref, abs=tolerance) == qy_conv
    assert pytest.approx(qz_ref, abs=tolerance) == qz_conv


@pytest.mark.parametrize(
    "quat",
    quat_test,
)
def test_quat2ypr2quat(quat):
    ypr = pyheadtracker.utils.quat2ypr(quat)
    quat_converted = pyheadtracker.utils.ypr2quat(ypr)

    # Wrap values close to 1 or -1 to avoid issues with sign ambiguity
    qw_ref = np.abs(quat.w) if np.abs(quat.w) - 1 < tolerance else quat.w
    qx_ref = np.abs(quat.x) if np.abs(quat.x) - 1 < tolerance else quat.x
    qy_ref = np.abs(quat.y) if np.abs(quat.y) - 1 < tolerance else quat.y
    qz_ref = np.abs(quat.z) if np.abs(quat.z) - 1 < tolerance else quat.z

    qw_conv = (
        np.abs(quat_converted.w)
        if np.abs(quat_converted.w) - 1 < tolerance
        else quat_converted.w
    )
    qx_conv = (
        np.abs(quat_converted.x)
        if np.abs(quat_converted.x) - 1 < tolerance
        else quat_converted.x
    )
    qy_conv = (
        np.abs(quat_converted.y)
        if np.abs(quat_converted.y) - 1 < tolerance
        else quat_converted.y
    )
    qz_conv = np.abs(quat.z) if np.abs(quat.z) - 1 < tolerance else quat.z

    # Assert that the result is close to the original value
    assert pytest.approx(qw_ref, abs=tolerance) == qw_conv
    assert pytest.approx(qx_ref, abs=tolerance) == qx_conv
    assert pytest.approx(qy_ref, abs=tolerance) == qy_conv
    assert pytest.approx(qz_ref, abs=tolerance) == qz_conv
