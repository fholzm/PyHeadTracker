import pyheadtracker as pht
from OpenGL import GL
import xr
from xr.utils.gl import ContextObject
from xr.utils.gl.glfw_util import GLFWOffscreenContextProvider

scenerotator_send = pht.out.IEMSceneRotator(ip="127.0.0.1", port=7000)
roomencoder_send = pht.out.IEMRoomEncoder(ip="127.0.0.1", port=7001, mode="listener")

with ContextObject(
    instance_create_info=xr.InstanceCreateInfo(
        enabled_extension_names=[
            # A graphics extension is mandatory (without a headless extension)
            xr.KHR_OPENGL_ENABLE_EXTENSION_NAME,
        ],
    ),
    context_provider=GLFWOffscreenContextProvider(),
) as context:
    # Create a head tracker using OpenXR
    ht = pht.hmd.openXR(context)

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

                    scenerotator_send.send_orientation(orientation)

                    orientation_ypr = pht.utils.quat2ypr(orientation).to_degrees()
                    print(
                        f"Yaw: {orientation_ypr[0]:7.2f} {orientation_ypr[1]:7.2f} {orientation_ypr[2]:7.2f}",
                        end="\r",
                    )

                if position is not None:
                    roomencoder_send.send_position(position)

                    # print(
                    #     f"XYZ: {position.x:7.2f} {position.y:7.2f} {position.z:7.2f}",
                    #     end="\r",
                    # )

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
