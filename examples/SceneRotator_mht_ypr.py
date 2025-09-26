from pyheadtracker import YPR, diy, out
from pyheadtracker import YPR
from pythonosc.udp_client import SimpleUDPClient

ht = diy.MrHeadTracker(
    device_name="MrHeadTracker:MrHeadTracker MIDI 1 24:0",
    orient_format="ypr",
)
ht.open()

osc_send = out.IEMSceneRotator(ip="127.0.0.1", port=7000)

while True:
    try:
        orientation = ht.read_orientation()
        osc_send.send_orientation(orientation)

        if isinstance(orientation, YPR):
            # Print the YPR values for debugging
            print(
                f"YPR: {orientation[0]:7.2f} {orientation[1]:7.2f} {orientation[2]:7.2f}",
                end="\r",
            )

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
        ht.close()
        break
