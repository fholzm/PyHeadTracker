# PyHeadTracker

This package provides an interface for interacting with head tracking hardware in Python.

The use of head trackers can greatly enhance the user experience in applications such as immersive audio, virtual reality, gaming, and assistive technologies. By providing precise head position and orientation data, developers can create more immersive and responsive environments for their users. However, interacting with different head trackers and their APIs can be a tedious process. `PyHeadTracker` aims to simplify this process by providing a unified interface for various head tracking devices in python.

## Overview

`PyHeadTracker` is designed to provide a simple and consistent interface for accessing head tracking data from various devices. The library abstracts the complexities of dealing with different hardware and APIs, allowing developers to focus on building their applications without worrying about the underlying details.

Typically, each head tracker is instantiated as object before opening the connection, e.g.

```python
from pyheadtracker import diy

ht = diy.MrHeadTracker(
    device_name="MrHeadTracker 1",
    orient_format="q",
)
ht.open()
```

Now you can access the head tracking data using the `read_orientation()` or `read_position()` method:

```python
while True:
    orientation = ht.read_orientation()

    if orientation is not None:
        w, x, y, z = orientation

        # Print the quaternion values for debugging
        print(f"WXYZ: {w:7.2f} {x:7.2f} {y:7.2f} {z:7.2f}", end="\r")
```

Orientation data is provided as `Quaternion` or `YPR` (yaw/pitch/roll) object, which can easily be converted to a list or NumPy array. when requesting the poition, a `Position` object is returned to access Cartesian coordinates.

Examples how to use this package can be found [here](https://git.iem.at/holzmueller/pyheadtracker/-/tree/main/examples?ref_type=heads).

## Supported devices

Currently the following head tracking devices are supported:

- [Supperware Head Tracker 1](https://supperware.co.uk/headtracker-overview)
- [IEM MrHeadTracker](https://git.iem.at/DIY/MrHeadTracker)
- Head mounted displays using [openXR](https://www.khronos.org/OpenXR/) (only on Windows/Linux)

If you are missing a device, feel free to contact us or open an [issue](https://git.iem.at/holzmueller/pyheadtracker/-/issues).

## Roadmap

In future releases, we plan to support additional head tracking devices and improve the overall functionality of the library. Some of the planned features include:

- Support for
  - SteamVR HMDs (e.g. HTC Vive)
  - webcam-based head tracking
  - OptiTrack

## License

This project is licensed under the [MIT License](https://git.iem.at/holzmueller/pyheadtracker/-/blob/main/LICENSE?ref_type=heads)
