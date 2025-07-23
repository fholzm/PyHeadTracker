import supperware
from pythonosc.udp_client import SimpleUDPClient

ip_out = "127.0.0.1"
port_out = 7000
client = SimpleUDPClient(ip_out, port_out)

ht = supperware.HeadTracker1(
    device_name="Head Tracker MIDI 1",
    refresh_rate=50,
    compass_on=True,
    orient_format="q",
)

ht.open(compass_force_calibration=False)

while True:
    try:
        orientation = ht.read_orientation()
        if orientation is not None:
            print("Orientation:", orientation)
            client.send_message(
                "/SceneRotator/quaternions",
                [orientation[0], -orientation[1], orientation[2], -orientation[3]],
            )
        else:
            print("Warning: No orientation data received.")

    except (EOFError, KeyboardInterrupt):
        print("\nBye.")
        ht.close()
        break
