===========================
Raspberry Pi Smart-ish Door
===========================

.. WARNING::

  2014/09/24: this project is not fully functional yet -- come back in
  a month or so.

.. IMPORTANT::

  IN CASE YOU MISSED THE "WARNING", THIS PROJECT IS CURRENTLY
  "PRE-ALPHA", WHICH MEANS IT DOES NOT WORK YET.

The `raspi-door` project comprises the GUI that is run on the
Raspberry PI on the inside of the door so that you can control your
door with *awesomeness*... or, as close as I can get it there.


Objectives
==========

Here are the list of raspi-door features that are implemented, going
to be implemented, and may be implemented.


Current Features
----------------

* Exterior door bell button and sound support
* Interior motion sensor and screen auto-on/off support
* Current time display
* Current weather display


Upcoming Features
-----------------

* Door lock/unlock control
* Bluetooth & WiFi connectivity access control
* Activity logging
* Door-event calendar integration
* Subway service alerts & ETAs


Potential Features
------------------

* Exterior camera with infrared lighting
* Biometrics: face/voice/fingerprint/etc recognition
* NFC/RFID support
* Remote door lock/unlock with camera feed
* Nefarious activity detector! YA MAN!


Raspi-Door Hardware
===================

TODO.


Raspi-Door Software
===================

.. code-block:: bash

  # (all commands as root *or* preceded with "sudo " *or* you
  #  know what you are doing... :-)

  # (optional) create a virtualenv for raspi-door
  $ virtualenv --prompt '(raspi-door) ' /path/to/virtualenv
  $ . /path/to/virtualenv/bin/activate

  # install pre-requisite pygame
  #   => not needed once issue #59 has been fixed:
  #     https://bitbucket.org/pygame/pygame/issues/59/pygame-and-pip
  # TODO: figure out why this is necessary...
  $ wget http://www.pygame.org/ftp/pygame-1.9.1release.tar.gz
  # IFF pygame disappears, there is a cache here:
    $ wget https://github.com/metagriffin/raspi-door/raw/master/cache/pygame-1.9.1release.tar.gz
  $ sudo apt-get install libsdl1.2-dev libsdl-image1.2-dev \
    libsdl-mixer1.2-dev libsdl-ttf2.0-dev \
    libsmpeg-dev libportmidi-dev
  $ ln -s ../libv4l1-videodev.h /usr/include/linux/videodev.h
  $ easy_install pygame-1.9.1release.tar.gz

  # install pre-requisite pgu
  # TODO: figure out why this is necessary...
  $ wget https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/pgu/pgu-0.18.zip
  # IFF pgu disappears, there is a cache here:
    $ wget https://github.com/metagriffin/raspi-door/raw/master/cache/pgu-0.18.zip
  $ easy_install pgu-0.18.zip

  $ pip install raspi-door

  # configure raspi-door
  $ raspi-door --initialize > /etc/raspi-door.conf
  $ nano /etc/raspi-door.conf
    # review all of the configuration options... and open a
    # raspi-door issue if anything is "unclear" :-)


Troubleshooting
===============

* ``"ImportError: No module named pkg_resources"``

  If you run into an issue during the install process and pip just
  doesn't work anymore, you may need to re-install
  setuptools. However, you need to do this without using `pip` or
  `easy_install`... so, check https://pypi.python.org/pypi/setuptools
  for direct installation details, i.e.:

  .. code-block:: bash

    $ wget https://bootstrap.pypa.io/ez_setup.py -O - | python


Credits
=======

* yuv2rgb_: Phil Burgess / Paint Your Dragon for Adafruit Industries
* picamera_: Dave Hughes


.. _yuv2rgb: https://github.com/adafruit/adafruit-pi-cam/blob/master/yuv2rgb.c
.. _picamera: https://pypi.python.org/pypi/picamera
