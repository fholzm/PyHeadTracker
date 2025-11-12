from pyheadtracker import supperware, out, Quaternion
import subprocess

osc_send = out.TASCAR(OSC_address="/demo/out", ip="127.0.0.1", port=9877)

ht = supperware.HeadTracker1(
    device_name="Head Tracker:Head Tracker MIDI 1 24:0",
    device_name_output="Head Tracker:Head Tracker MIDI 1 24:0",
    refresh_rate=50,
    compass_on=True,
    orient_format="q",
)
ht.open(compass_force_calibration=False)
ht.zero()

tascar = subprocess.Popen(["tascar", "tascar.tsc"])

while True:
    try:
        orientation = ht.read_orientation()

        if isinstance(orientation, Quaternion):
            osc_send.send_orientation(orientation)
            # Print the quaternion values for debugging
            print(
                f"WXYZ: {orientation[0]:7.2f} {orientation[1]:7.2f} {orientation[2]:7.2f} {orientation[3]:7.2f}",
                end="\r",
            )

    except (EOFError, KeyboardInterrupt):
        print("\nClosing connection.")
        ht.close()
        tascar.terminate()
        break
