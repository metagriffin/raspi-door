===========================
Raspberry Pi Smart-ish Door
===========================

.. WARNING::

  2014/05/13: this project is brand-spanking new, so it is most
  **definitely** not ready for use. Come back in a month or so.

.. IMPORTANT::

  IN CASE YOU MISSED THE "WARNING", THIS PROJECT IS CURRENTLY
  "PRE-ALPHA", WHICH MEANS IT DOES NOT WORK YET.

The `raspi-door` project comprises the GUI that is run on the
Raspberry PI on the inside of the door so that you can control your
door with *awesomeness*... or, as close as I can get it there.

But first you need to setup the hardware.


Raspi-Door Hardware
===================

TODO.


Raspi-Door Software
===================

If you want to play with the GUI on Windows or Mac: install the
wxPython 3.0 with Python 2.7 binaries linked to from
`http://wxpython.org/download.php`_. Then, on the command line, type:

.. code-block:: bash

  $ pip install raspi-door
  $ raspi-door --mock

TODO: create ``.exe`` and ``.dmg`` downloads for Windows and Mac
users...

Install on Linux/Raspberry PI:

.. code-block:: bash

  # install wxPython 3.0.0.0

  $ wget http://downloads.sourceforge.net/project/wxpython/wxPython/3.0.0.0/wxPython-src-3.0.0.0.tar.bz2
  $ tar xvjf wxPython-src-3.0.0.0.tar.bz2
  $ cd wxPython-src-3.0.0.0/wxPython
  # warning: the next step can take a *very* long time...
  $ python build-wxpython.py --install
    # if building into a virtualenv, add " --installdir=$VIRTUAL_ENV" to the last line
    # and set your LD_LIBRARY_PATH to include "$VIRTUAL_ENV/usr/local/lib"

  $ pip install raspi-door
  $ raspi-door

TODO: create ``.deb`` downloads...


Credits
=======

* yuv2rgb_: Phil Burgess / Paint Your Dragon for Adafruit Industries
* picamera_: Dave Hughes


.. _yuv2rgb: https://github.com/adafruit/adafruit-pi-cam/blob/master/yuv2rgb.c
.. _picamera: https://pypi.python.org/pypi/picamera
