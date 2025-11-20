import pyheadtracker as pht

ht = pht.cam.MPFaceLandmarker(0)
ht.open()

while True:
    try:
        pose = ht.read_pose()

        if pose is None:
            continue

        orientation = oreintation = pose["orientation"]
        position = pose["position"]

        if isinstance(orientation, pht.Quaternion):
            orientation_q = orientation
            orientation_ypr = pht.utils.quat2ypr(orientation_q).to_degrees()

        if isinstance(orientation, pht.YPR):
            orientation_q = pht.utils.ypr2quat(orientation)
            orientation_ypr = orientation.to_degrees()

        if orientation is not None and position is not None:
            print(
                f"Position: {position[0]:7.2f} m, {position[1]:7.2f} m, {position[2]:7.2f} m    |    YPR: {orientation_ypr[0]:7.2f}°, {orientation_ypr[1]:7.2f}°, {orientation_ypr[2]:7.2f}°",
                end="\r",
            )

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
        ht.close()
        break
