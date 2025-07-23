import supperware
from pythonosc.udp_client import SimpleUDPClient

ip_out = "127.0.0.1"
port_out = 7000
client = SimpleUDPClient(ip_out, port_out)

ht = supperware.HeadTracker1(
    device_name="Head Tracker",
    refresh_rate=50,
    compass_on=True,
    orient_format="q",
)

ht.open(compass_force_calibration=False)
ht.zero()

while True:
    try:
        orientation = ht.read_orientation()
        if orientation is not None:
            w, x, y, z = orientation
            client.send_message("/SceneRotator/quaternions", [w, -y, x, -z])
            # Print the quaternion values for debugging
            # print(f"WXYZ: {w:7.2f} {x:7.2f} {y:7.2f} {z:7.2f}", end="\r")
        else:
            print("Warning: No orientation data received.")

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
        ht.close()
        break
