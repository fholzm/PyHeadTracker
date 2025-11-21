import pyheadtracker as pht

osc_send = pht.out.IEMSceneRotator(ip="127.0.0.1", port=7000)

ht = pht.cam.MPFaceLandmarker(0, orient_format="ypr")

ht.open()
ht.zero()

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
