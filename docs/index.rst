PyHeadTracker documentation
===========================

This package provides an interface for interacting with head tracking hardware in Python.

The use of head trackers can greatly enhance the user experience in applications such as immersive audio, virtual reality, gaming, and assistive technologies. By providing precise head position and orientation data, developers can create more immersive and responsive environments for their users. However, interacting with different head trackers and their APIs can be a tedious process. `PyHeadTracker` aims to simplify this process by providing a unified interface for various head tracking devices in python.


.. toctree::
   :caption: Contents:
   :maxdepth: 2

   Home <self>
   api


Installation
------------

The package can be installed via pip: ::

  pip install pyheadtracker


Supported devices
-----------------

- `Supperware Head Tracker 1 <https://supperware.co.uk/headtracker-overview>`_
- `IEM MrHeadTracker <https://git.iem.at/DIY/MrHeadTracker>`_
- Head mounted displays using `openXR <https://www.khronos.org/OpenXR/>`_ (only on Windows/Linux)


If you are missing a device, feel free to contact us or open an `issue <https://git.iem.at/holzmueller/pyheadtracker/-/issues>`_.


Roadmap
-------

In future releases, we plan to support additional head tracking devices and improve the overall functionality of the library. Some of the planned features include:

- Support for
   - SteamVR HMDs (e.g. HTC Vive)
   - webcam-based head tracking
   - OptiTrack
- Dedicated module to send head tracking data over OSC to common targets and renderers


Source Code
-----------

Development happens on the `IEM's  GitLab instance <https://git.iem.at/holzmueller/pyheadtracker/>`_. The repository is mirrored to `GitHub <https://github.com/fholzm/PyHeadTracker>`_ as well to make forking and contributing easier.


License
-------

PyHeadTracker is licensed under the `MIT License <https://git.iem.at/holzmueller/pyheadtracker/-/blob/main/LICENSE?ref_type=heads>`_.
