import pyheadtracker as pht

ht = pht.diy.MrHeadTracker(
    device_name="MrHeadTracker:MrHeadTracker MIDI 1 24:0",
    orient_format="ypr",
)
ht.open()

osc_send = pht.out.IEMSceneRotator(ip="127.0.0.1", port=7000)

while True:
    try:
        orientation = ht.read_orientation()

        if isinstance(orientation, pht.YPR):
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
