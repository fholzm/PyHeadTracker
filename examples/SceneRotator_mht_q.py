from pyheadtracker import iem
from pythonosc.udp_client import SimpleUDPClient

ip_out = "127.0.0.1"
port_out = 7000
client = SimpleUDPClient(ip_out, port_out)

ht = iem.MrHeadTracker(
    device_name="APRteacher",
    orient_format="q",
)
ht.open()


while True:
    try:
        orientation = ht.read_orientation()
        if len(orientation) == 4:
            w, x, y, z = orientation
            client.send_message("/SceneRotator/quaternions", [w, -x, y, -z])

            # Print the quaternion values for debugging
            print(f"WXYZ: {w:7.2f} {x:7.2f} {y:7.2f} {z:7.2f}", end="\r")

    except (EOFError, KeyboardInterrupt):
        ht.close()
        print("\nClosing connection.")
        break
