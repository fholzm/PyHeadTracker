import pytest
import numpy as np
import pyheadtracker

quat_test = [
    pyheadtracker.Quaternion(1, 0, 0, 0),
    pyheadtracker.Quaternion(0, 1, 0, 0),
    pyheadtracker.Quaternion(0, 0, 1, 0),
    pyheadtracker.Quaternion(0, 0, 0, 1),
    pyheadtracker.Quaternion(0.7071, 0.7071, 0, 0),
    pyheadtracker.Quaternion(0.7071, 0, 0.7071, 0),
    pyheadtracker.Quaternion(0.7071, 0, 0, 0.7071),
    pyheadtracker.Quaternion(0.5, 0.5, 0.5, 0.5),
]

# TODO: Check sequence of ypr angles
ypr_test = [
    pyheadtracker.YPR(0, 0, 0),
    pyheadtracker.YPR(0, 0, np.pi),
    pyheadtracker.YPR(np.pi, 0, np.pi),
    pyheadtracker.YPR(np.pi, 0, 0),
    pyheadtracker.YPR(0, 0, np.pi / 2),
    pyheadtracker.YPR(0, -np.pi / 2, 0),
    pyheadtracker.YPR(np.pi / 2, 0, 0),
    pyheadtracker.YPR(np.pi / 2, 0, np.pi / 2),
]


@pytest.mark.parametrize(
    "quat, ypr",
    list(zip(quat_test, ypr_test)),
)
def test_quat2ypr(quat, ypr):
    ypr_converted = pyheadtracker.utils.quat2ypr(quat)

    # Assert that the result is close to the expected value
    assert pytest.approx(ypr[0], rel=1e-4) == ypr_converted[0]
    assert pytest.approx(ypr[1], rel=1e-4) == ypr_converted[1]
    assert pytest.approx(ypr[2], rel=1e-4) == ypr_converted[2]


@pytest.mark.parametrize(
    "quat, ypr",
    list(zip(quat_test, ypr_test)),
)
def test_ypr2quat(quat, ypr):
    quat_converted = pyheadtracker.utils.ypr2quat(ypr)

    # Assert that the result is close to the expected value
    assert pytest.approx(quat.w, rel=1e-4) == quat_converted.w
    assert pytest.approx(quat.x, rel=1e-4) == quat_converted.x
    assert pytest.approx(quat.y, rel=1e-4) == quat_converted.y
    assert pytest.approx(quat.z, rel=1e-4) == quat_converted.z


@pytest.mark.parametrize(
    "quat",
    quat_test,
)
def test_quat2ypr2quat(quat):
    ypr = pyheadtracker.utils.quat2ypr(quat)
    quat_converted = pyheadtracker.utils.ypr2quat(ypr)

    # Assert that the result is close to the original value
    assert pytest.approx(quat.w, rel=1e-4) == quat_converted.w
    assert pytest.approx(quat.x, rel=1e-4) == quat_converted.x
    assert pytest.approx(quat.y, rel=1e-4) == quat_converted.y
    assert pytest.approx(quat.z, rel=1e-4) == quat_converted.z
