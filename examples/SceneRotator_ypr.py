import supperware
from pythonosc.udp_client import SimpleUDPClient

ip_out = "127.0.0.1"
port_out = 7000
client = SimpleUDPClient(ip_out, port_out)

ht = supperware.HeadTracker1(
    device_name="Head Tracker MIDI 1",
    refresh_rate=50,
    compass_on=True,
    orient_format="ypr",
)

ht.open(compass_force_calibration=False)

while True:
    try:
        orientation = ht.read_orientation()
        if orientation is not None:
            orientation *= 180 / 3.141592653589793  # Convert radians to degrees
            client.send_message(
                "/SceneRotator/ypr", [-orientation[0], orientation[1], -orientation[2]]
            )
        else:
            print("Warning: No orientation data received.")

    except (EOFError, KeyboardInterrupt):
        print("\nBye.")
        ht.close()
        break
