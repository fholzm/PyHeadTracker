Usage
========

This guide will help you understand how to set up and use PyHeadTracker in your own projects. You can find examples and detailed API documentation in the respective sections.

Hardware Setup
--------------

Be sure to connect a supported head tracking device to your computer before running the software. Follow the manufacturer's instructions for setting up the hardware. Many head trackers provide data in MIDI format via USB, e.g. the IEM MrHeadTracker or Supperware Head Tracker 1. Keep in mind, that Windows only allows a single application to access the MIDI device at a time, so you may close other applications before running your script.

To use the openXR bindings, you need to have the respective openXR runtime installed.


Create and open
---------------

At first, import the package as

.. code-block:: python

    import pyheadtracker

Now you can create a head tracker object, in this example the `MrHeadTracker`. The device name as well as the output format (`Quaternion` or `YPR` (yaw/pitch/roll)) can be specified for each tracker. Some devices may allow additional configuration options. Linux and Windows tend to append indices to the device name, so the error returns the available devices if the specified name is not found.

.. code-block:: python

    ht = pyheadtracker.diy.MrHeadTracker(
        device_name="MrHeadTracker",
        orient_format="q",
    )

After the object is instatiated, the connection can be opened.

.. code-block:: python

    ht.open()

Getting data
------------

Some devices can be zeroed to set the current orientation as the new reference point. This can be done by calling the `zero()` method.

.. code-block:: python

    ht.zero()

To retrieve data from the head tracker, you can use the `read_orientation()` or `read_position()` method. This method returns the current orientation data in the specified format. Note that not all devices provide position data.

.. code-block:: python

    orientation = ht.read_orientation()

    if orientation is not None:
        print(orientation)
    else:
        print("No data available")


Close connection
----------------

It is best to close the connection gracefully after use. This can be done by calling the `close()` method.

.. code-block:: python

    ht.close()
