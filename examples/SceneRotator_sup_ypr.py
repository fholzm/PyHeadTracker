from pyheadtracker import supperware, out, YPR
from pythonosc.udp_client import SimpleUDPClient

osc_send = out.IEMSceneRotator(ip="127.0.0.1", port=7000)


ht = supperware.HeadTracker1(
    device_name="Head Tracker 1",
    device_name_output="Head Tracker 2",
    refresh_rate=50,
    compass_on=True,
    orient_format="ypr",
)

ht.open(compass_force_calibration=False)
ht.zero()

while True:
    try:
        orientation = ht.read_orientation()

        if isinstance(orientation, YPR):
            osc_send.send_orientation(orientation)
            # Print the YPR values for debugging
            print(
                f"YPR: {orientation[0]:7.2f} {orientation[1]:7.2f} {orientation[2]:7.2f}",
                end="\r",
            )

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
        ht.close()
        break
