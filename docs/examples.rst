Examples
========

These examples may help you get started with PyHeadTracker. You can find more `here <https://git.iem.at/holzmueller/pyheadtracker/-/tree/main/examples?ref_type=heads>`__.


Supperware
----------

This example demonstrates how to use the Supperware Head Tracker with PyHeadTracker and send the orientation data via OSC to the `IEM SceneRotator <https://plugins.iem.at/docs/plugindescriptions/#scenerotator>`__.

.. code-block:: python

    import pyheadtracker as pht

    osc_send = pht.out.IEMSceneRotator(ip="127.0.0.1", port=7000)

    ht = pht.supperware.HeadTracker1(
        device_name="Head Tracker 1",
        device_name_output="Head Tracker 2",
        refresh_rate=50,
        compass_on=True,
        orient_format="q",
    )

    ht.open(compass_force_calibration=False)
    ht.zero()

    while True:
        try:
            orientation = ht.read_orientation()

            if isinstance(orientation, pht.Quaternion):
                osc_send.send_orientation(orientation)
                # Print the quaternion values for debugging
                print(
                    f"WXYZ: {orientation[0]:7.2f} {orientation[1]:7.2f} {orientation[2]:7.2f} {orientation[3]:7.2f}",
                    end="\r",
                )

        except (EOFError, KeyboardInterrupt):
            print("\nClosing connection.")
            ht.close()
            break
            

Camera-based tracking
---------------------
This example demonstrates how to use the MediaPipe Face Landmarker for webcam-based head tracking with PyHeadTracker. The orientation data is sent via OSC to the `IEM SceneRotator <https://plugins.iem.at/docs/plugindescriptions/#scenerotator>`__.

.. code-block:: python

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


openXR
------

In this example, we use the openXR bindings to retrieve head tracking data from a head mounted display, while rendering a dummy OpenGL scene. Orientation data is sent via OSC to the `IEM SceneRotator <https://plugins.iem.at/docs/plugindescriptions/#scenerotator>`__ and position data to the `IEM RoomEncoder <https://plugins.iem.at/docs/plugindescriptions/#roomencoder>`__.

.. code-block:: python

    from OpenGL import GL
    import numpy as np
    import pyheadtracker
    import xr
    from xr.utils.gl import ContextObject
    from pythonosc.udp_client import SimpleUDPClient

    client_scenerotator = SimpleUDPClient("127.0.0.1", 7000)
    client_roomencoder = SimpleUDPClient("127.0.0.1", 7001)


    with ContextObject(
        instance_create_info=xr.InstanceCreateInfo(
            enabled_extension_names=[
                # A graphics extension is mandatory (without a headless extension)
                xr.KHR_OPENGL_ENABLE_EXTENSION_NAME,
            ],
        ),
    ) as context:
        # Create a head tracker object using OpenXR
        ht = pyheadtracker.hmd.openXR(context)

        eye_colors = [
            (0, 1, 0, 1),  # Left eye green
            (0, 0, 1, 1),  # Right eye blue
            (1, 0, 0, 1),  # Third eye blind
        ]

        run_idx = 0

        try:
            for frame_index, frame_state in enumerate(context.frame_loop()):
                for view_index, view in enumerate(context.view_loop(frame_state)):
                    run_idx += 1

                    if run_idx == 20:
                        ht.zero()  # Reset orientation after a few frames

                    # Render dummy data
                    GL.glClearColor(*eye_colors[view_index])
                    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                    # Read orientation and position
                    orientation = ht.read_orientation(frame_state)
                    position = ht.read_position(frame_state)

                    # Send orientation and position to SceneRotator and RoomEncoder
                    if orientation is not None:
                        w, x, y, z = orientation
                        client_scenerotator.send_message(
                            "/SceneRotator/quaternions", [w, -x, y, -z]
                        )
                        print(f"WXYZ: {w:7.2f} {x:7.2f} {y:7.2f} {z:7.2f}", end="\r")

                    if position is not None:
                        x, y, z = position
                        client_roomencoder.send_message("/RoomEncoder/listenerX", x)
                        client_roomencoder.send_message("/RoomEncoder/listenerY", y)
                        client_roomencoder.send_message("/RoomEncoder/listenerZ", z)

        except (EOFError, KeyboardInterrupt):
            print("\nClosing connection.")