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
import atexit
import pygame
import re
import asset
import six

from .service import Service
from .trap import Trap

try:
  import RPi.GPIO as GPIO
except RuntimeError:
  GPIO = None

#------------------------------------------------------------------------------
log = logging.getLogger(__name__)

DEFAULT_EVENT_ACTION = {
  'bell.pressed.play' : 'raspi_door:res/audio/doorbell.ogg',
}

isAssetSpec = re.compile('^[a-z][a-z0-9_]*:', re.IGNORECASE)

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
    self.motion   = False
    self._led     = False
    self.ledpin   = int(self.getConfig('gpio.led', '18'))
    self.pirpin   = int(self.getConfig('gpio.pir', '22'))
    self.btnpin   = int(self.getConfig('gpio.button', '23'))
    self.sounds   = dict()
    self.on(':', self.onSense)
    if not self.mock:
      self.startGpio()
    else:
      self.thread = threading.Thread(
        name='raspi_door.sensor.SensorService', target=self.runMockSense)
      self.thread.daemon = True
      self.thread.start()
    return self

  #----------------------------------------------------------------------------
  def startGpio(self):
    if not GPIO:
      raise RuntimeError('Raspberry PI\'s GPIO not available')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.btnpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(self.ledpin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(self.pirpin, GPIO.IN)
    atexit.register(GPIO.cleanup)
    btime = int(1000 * float(self.getConfig('bell.debounce', 0.2)))
    GPIO.add_event_detect(self.btnpin, GPIO.FALLING, callback=self.onBellPressed, bouncetime=btime)
    GPIO.add_event_detect(self.pirpin, GPIO.BOTH,  callback=self.onMotionDetected)

  @property
  def led(self):
    return self._led

  @led.setter
  def led(self, value):
    self._led = bool(value)
    GPIO.output(self.ledpin, self._led)

  #----------------------------------------------------------------------------
  def onBellPressed(self, *args, **kw):
    self.trigger('bell', 'pressed')

  #----------------------------------------------------------------------------
  def onMotionDetected(self, *args, **kw):
    self.trigger('motion', 'started' if GPIO.input(self.pirpin) else 'stopped')

  #----------------------------------------------------------------------------
  def onSense(self, topic, event, *args, **kw):
    if topic == 'motion':
      self.motion = event == 'started'
    self.app.shellexec(self.getConfig(topic + '.' + event + '.exec', None))
    evt = topic + '.' + event + '.play'
    if evt not in self.sounds:
      # todo: support defaulting to ``raspi_door:res/audio/doorbell.ogg``...
      play = self.getConfig(evt, DEFAULT_EVENT_ACTION.get(evt, None))
      if play and isAssetSpec.match(play):
        play = six.BytesIO(asset.load(play).read())
      if play:
        self.sounds[evt] = pygame.mixer.Sound(play)
    if evt in self.sounds:
      self.sounds[evt].play()

  #----------------------------------------------------------------------------
  def run(self):
    pass

  #----------------------------------------------------------------------------
  def runMockSense(self):
    while True:
      try:
        self.mockSense()
      except Exception:
        log.exception('error while waiting for sense events')
        time.sleep(10)

  #----------------------------------------------------------------------------
  def mockSense(self):
    sense = raw_input('Emulate sensor (b=bell, m=motion, l=lock, n=nfc): ')
    lut = dict(
      b = ('bell', 'pressed'),
      m = ('motion', 'started'),
      l = ('lock', 'pressed'),
      n = ('nfc', 'read'),
    )
    if sense not in lut:
      print '[**] invalid sensor "%s"... ignoring' % (sense,)
      return
    event = lut[sense]
    self.trigger(*event)
    if event[0] == 'motion':
      threading.Timer(5, self.trigger, ['motion', 'stopped']).start()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
