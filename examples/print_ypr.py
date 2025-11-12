import pyheadtracker as pht

# ht = pht.supperware.HeadTracker1(
#     device_name="Head Tracker:Head Tracker MIDI 1 24:0",
#     device_name_output="Head Tracker:Head Tracker MIDI 1 24:0",
#     refresh_rate=100,
#     compass_on=True,
#     orient_format="q",
# )
# ht.open(compass_force_calibration=False)
# ht.zero()

ht = pht.diy.MrHeadTracker(
    device_name="MrHeadTracker:MrHeadTracker MIDI 1 24:0",
    orient_format="q",
    inverse=False,
)
ht.open()

while True:
    try:
        orientation = ht.read_orientation()

        if isinstance(orientation, pht.Quaternion):
            orientation_q = orientation
            orientation_ypr = pht.utils.quat2ypr(orientation_q).to_degrees()

        if isinstance(orientation, pht.YPR):
            orientation_q = pht.utils.ypr2quat(orientation)
            orientation_ypr = orientation.to_degrees()

        if isinstance(orientation, (pht.Quaternion, pht.YPR)):
            print(
                f"WXYZ: {orientation_q[0]:7.2f}, {orientation_q[1]:7.2f}, {orientation_q[2]:7.2f}, {orientation_q[3]:7.2f}    |    YPR: {orientation_ypr[0]:7.2f}, {orientation_ypr[1]:7.2f}, {orientation_ypr[2]:7.2f}",
                end="\r",
            )

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
        ht.close()
        break
