# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/06/26
# copy: (C) Copyright 2014-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import os
import time
import threading
import logging
import morph
import subprocess
import atexit

from .service import Service
from .trap import Trap

try:
  import RPi.GPIO as GPIO
except RuntimeError:
  GPIO = None

#------------------------------------------------------------------------------
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class SensorService(Service, Trap):

  section = 'sensor'

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(SensorService, self).__init__(*args, **kw)

  #----------------------------------------------------------------------------
  def start(self):
    self.next     = None
    self.mock     = morph.tobool(self.getConfig('mock', 'false'))
    self.ledpin   = int(self.getConfig('gpio.led', '18'))
    self.pirpin   = int(self.getConfig('gpio.pir', '22'))
    self.btnpin   = int(self.getConfig('gpio.button', '23'))
    self.on(':', self.onSense)
    if not self.mock:
      self.startGpio()

    self.thread   = threading.Thread(
      name='raspi_door.sensor.SensorService', target=self.runBackground)
    self.thread.daemon = True
    self.thread.start()
    return self

  #----------------------------------------------------------------------------
  def startGpio(self):
    if not GPIO:
      raise RuntimeError('Raspberry PI\'s GPIO not available')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.btnpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(self.ledpin, GPIO.OUT, initial=GPIO.HIGH)
    atexit.register(GPIO.cleanup)

  #----------------------------------------------------------------------------
  def onSense(self, topic, event, *args, **kw):
    run = self.getConfig(topic + '.' + event + '.exec', 'bling')
    if run:
      # todo: make this a little less "suppressive"...
      if not self.mock:
        GPIO.output(self.ledpin, False)
      subprocess.call(run + ' > /dev/null 2>&1', shell=True, close_fds=True)
      if not self.mock:
        GPIO.output(self.ledpin, True)

  #----------------------------------------------------------------------------
  def run(self):
    pass

  #----------------------------------------------------------------------------
  def runBackground(self):
    while True:
      try:
        self.sense()
      except Exception:
        log.exception('error while waiting for sense events')
        time.sleep(10)

  #----------------------------------------------------------------------------
  def sense(self):
    if self.mock:
      return self.mockSense()
    ## todo: listen for motion too...
    ## todo: use this instead?...
    ##   GPIO.add_event_detect(self.btnpin, GPIO.FALLING, callback=self.onBellPressed)
    GPIO.wait_for_edge(self.btnpin, GPIO.FALLING)
    self.trigger('bell', 'pressed')

  #----------------------------------------------------------------------------
  def mockSense(self):
    sense = raw_input('Emulate sensor (b=bell, m=motion, l=lock, n=nfc): ')
    lut = dict(
      b = ('bell', 'pressed'),
      m = ('motion', 'detected'),
      l = ('lock', 'pressed'),
      n = ('nfc', 'read'),
    )
    if sense not in lut:
      print '[**] invalid sensor "%s"... ignoring' % (sense,)
      return
    event = lut[sense]
    self.trigger(*event)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
