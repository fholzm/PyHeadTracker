import pyheadtracker as pht

scenerotator_send = pht.out.IEMSceneRotator(ip="127.0.0.1", port=7000)
roomencoder_send = pht.out.IEMRoomEncoder(ip="127.0.0.1", port=7001, mode="listener")

ht = pht.cam.MPFaceLandmarker(0, orient_format="ypr")

ht.open()
ht.zero()

while True:
    try:
        pose = ht.read_pose()

        if pose is not None:
            orientation = pose["orientation"]
            position = pose["position"]
        else:
            continue

        if isinstance(orientation, pht.YPR):
            scenerotator_send.send_orientation(orientation)

        if isinstance(position, pht.Position):
            roomencoder_send.send_position(position)

        if isinstance(orientation, pht.YPR) and isinstance(position, pht.Position):
            print(
                f"Yaw: {orientation.yaw:.2f}, Pitch: {orientation.pitch:.2f}, Roll: {orientation.roll:.2f} | X: {position.x:.2f}, Y: {position.y:.2f}, Z: {position.z:.2f}",
                end="\r",
            )

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
        ht.close()
        break
