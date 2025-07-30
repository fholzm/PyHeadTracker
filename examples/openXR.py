from OpenGL import GL
import numpy as np
import pyheadtracker
import xr
from pythonosc.udp_client import SimpleUDPClient

client_scenerotator = SimpleUDPClient("127.0.0.1", 7000)
client_roomencoder = SimpleUDPClient("127.0.0.1", 7001)


with xr.ContextObject(
    instance_create_info=xr.InstanceCreateInfo(
        enabled_extension_names=[
            # A graphics extension is mandatory (without a headless extension)
            xr.KHR_OPENGL_ENABLE_EXTENSION_NAME,
        ],
    ),
) as context:
    # Create a head tracker using OpenXR
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
                    ht.zero()
                GL.glClearColor(*eye_colors[view_index])
                GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                orientation = ht.read_orientation(frame_state)
                position = ht.read_position(frame_state)

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
                    # print(f"XYZ: {x:7.2f} {y:7.2f} {z:7.2f}", end="\r")

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
