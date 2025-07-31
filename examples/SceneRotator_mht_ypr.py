from pyheadtracker import iem
from pyheadtracker import YPR
from pythonosc.udp_client import SimpleUDPClient

ip_out = "127.0.0.1"
port_out = 7000
client = SimpleUDPClient(ip_out, port_out)

ht = iem.MrHeadTracker(
    device_name="MrHeadTracker 1",
    orient_format="ypr",
)
ht.open()

while True:
    try:
        orientation = ht.read_orientation()
        if isinstance(orientation, YPR):
            y, p, r = orientation.to_degrees()  # Convert radians to degrees
            client.send_message("/SceneRotator/ypr", [-y, p, -r])
            # Print the YPR values for debugging
            print(f"YPR: {-y:7.2f} {p:7.2f} {-r:7.2f}", end="\r")
        else:
            print("Warning: No orientation data received.")

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
        ht.close()
        break
