# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/05/07
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
import six
import time
import threading
import pygame
import atexit
try:
  import warnings
  warnings.filterwarnings('ignore')
  import picamera
except RuntimeError:
  picamera = None
finally:
  warnings.resetwarnings()
from aadict import aadict
import morph
import smoke
# import yuv2rgb
from pgu import gui
import logging
from six.moves import configparser as CP

from .i18n import _
from . import lock, camera, event, trap
from . import ui
from .clock import ClockService
from .weather import WeatherService
from .alert import AlertService
from .sensor import SensorService

#------------------------------------------------------------------------------
CaptureEvent = event.newEvent()
log = logging.getLogger(__name__)

# #------------------------------------------------------------------------------
# class CameraCaptureThread(threading.Thread):

#   #----------------------------------------------------------------------------
#   def __init__(self, app, *args, **kw):
#     super(CameraCaptureThread, self).__init__(*args, **kw)
#     self.app      = app
#     self._running = False
#     self._cond    = threading.Condition()
#     self._timeout = 1.0 / float(self.app.getConfig('fps', 10, section='camera'))

#   #----------------------------------------------------------------------------
#   @property
#   def running(self):
#     with self._cond:
#       return self._running
#   @running.setter
#   def running(self, value):
#     with self._cond:
#       self._running = value
#       self._cond.notify()

#   #----------------------------------------------------------------------------
#   def run(self):
#     while True:
#       with self._cond:
#         if not self._running:
#           self._cond.wait()
#           continue
#         self.capture()
#         self._cond.wait(self._timeout)

#   #----------------------------------------------------------------------------
#   def capture(self):
#     # todo: make this `resize` depend on the screen...
#     buf = six.BytesIO()
#     size = self.app.camera.resolution
#     data = self.app.camera.capture(buf, use_video_port=True, format='png',
#                                    resize=size, thumbnail=None)
#     # todo: check what the picamera.capture() returns...
#     if data is None:
#       img = pygame.image.load(buf).convert()
#     else:
#       img = pygame.image.fromstring(data, size, 'RGB')
#     # self._buf.readinto(self._yuv)
#     # yuv2rgb.convert(self._yuv, self._rgb, 240, 180)
#     # img = pygame.image.frombuffer(rgb[0:
#     #   (sizeData[sizeMode][1][0] * sizeData[sizeMode][1][1] * 3)],
#     #   sizeData[sizeMode][1], 'RGB')
#     pygame.fastevent.post(CaptureEvent(image=img))

# sizeData = [ # Camera parameters for different size settings
#  # Full res      Viewfinder  Crop window
#  [(2592, 1944), (320, 240), (0.0   , 0.0   , 1.0   , 1.0   )], # Large
#  [(1920, 1080), (320, 180), (0.1296, 0.2222, 0.7408, 0.5556)], # Med

#------------------------------------------------------------------------------
class App(object):

  #----------------------------------------------------------------------------
  def __init__(self, options):
    self.state    = trap.AttributeTrap()
    self.sleeper  = None
    self.services = []
    self.options  = aadict(vars(options))
    self.options.geometry = self.options.geometry or 'fullscreen'
    if self.options.geometry == 'fullscreen':
      self.options.geometry = None
    else:
      self.options.geometry = tuple(
        [int(e) for e in self.options.geometry.split('x')])
    self.options.mock   = morph.tobool(self.options.mock)
    self.options.locale = self.options.locale or 'en'
    if self.options.mock:
      self.weather  = None # todo
      self.calendar = None # todo
    else:
      self.weather  = None # todo
      self.calendar = None # todo

  #----------------------------------------------------------------------------
  def getConfig(self, option, default=None, section='gui', raw=False):
    try:
      return self.options.config.get(section, option, raw=raw)
    except (CP.NoSectionError, CP.NoOptionError) as err:
      return default

  #----------------------------------------------------------------------------
  # todo: is there a way to mark this as a "cacheable" property?...
  @property
  def resdir(self):
    return os.path.join(os.path.dirname(__file__), 'res')

  #----------------------------------------------------------------------------
  def start(self):
    self.initUI()
    self.sensors = SensorService(self).start()
    self.services.append(ClockService(self).start())
    self.services.append(WeatherService(self).start())
    self.services.append(AlertService(self).start())
    self.services.append(self.sensors)
    # self.initCamera()
    self.initLock()
    # self.draw()

    self.sensors.on(':', self.sensorAction)

    self.mainLoop()

  #----------------------------------------------------------------------------
  def sensorAction(self, topic, event, *args, **kw):
    print 'SENSOR: ',topic,'=>',event
    self.wake()
    if topic in ('bell', 'lock', 'nfc'):
      self.state.showcam = True

  #----------------------------------------------------------------------------
  def wake(self):
    self.state.showscreen = True
    # TODO: protect with mutexes!...
    if self.sleeper:
      self.sleeper.cancel()
    self.sleeper = threading.Timer(
      float(self.getConfig('sleep', section='screen', default=10)),
      self.sleep)
    self.sleeper.daemon = True
    self.sleeper.start()

  #----------------------------------------------------------------------------
  def sleep(self):
    # TODO: protect with mutexes!...
    # TODO: check to see if the motion sensor is still triggering... if so
    #       wait sleep / 2 longer...
    self.state.showscreen = False

  #----------------------------------------------------------------------------
  def onShowScreen(self, old, new, **kw):
    if new:
      # note: this is to reset the sleeper timer
      self.wake()
    print 'SCREEN-SHOW:',repr(new),'<=',repr(old)
    # TODO...

  #----------------------------------------------------------------------------
  def initUI(self):
    pygame.init()
    pygame.fastevent.init()
    pygame.display.set_caption(_('Door Controller'))
    if not self.options.mock:
      pygame.mouse.set_visible(False)
    self.form   = gui.Form()
    if not self.options.geometry:
      self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
      self.screen = pygame.display.set_mode(self.options.geometry)
    # todo: how to convert theme to use pkg_resources?...
    self.pguapp = gui.App(theme=gui.Theme(os.path.join(self.resdir, 'theme')))
    # todo: get the current size...
    self.ui     = ui.UI(self, width=240, height=320)
    self.pguapp.connect(pygame.QUIT, self.pguapp.quit, None)
    self.pguapp.init(self.ui)
    # register button callbacks
    self.ui.find('btn-alert').connect(gui.CLICK, self.onButtonAlert)
    self.ui.find('btn-weather').connect(gui.CLICK, self.onButtonWeather)
    self.ui.find('btn-exit').connect(gui.CLICK, self.onButtonExit)
    self.ui.find('btn-unlock').connect(gui.CLICK, self.onButtonUnlock)
    self.ui.find('btn-lock').connect(gui.CLICK, self.onButtonLock)
    self.ui.find('btn-permlock').connect(gui.CLICK, self.onButtonPermLock)
    self.ui.find('btn-info').connect(gui.CLICK, self.onButtonInfo)

    # self.state.on('showcam:changed', self.onShowCamera)
    # self.state.showcam = False

    self.ui.find('btn-alert').connect(gui.CLICK, self.onButtonAlert)
    self.ui.find('btn-weather').connect(gui.CLICK, self.onButtonWeather)
    self.ui.find('btn-exit').connect(gui.CLICK, self.onButtonExit)
    self.ui.find('btn-unlock').connect(gui.CLICK, self.onButtonUnlock)
    self.ui.find('btn-lock').connect(gui.CLICK, self.onButtonLock)
    self.ui.find('btn-permlock').connect(gui.CLICK, self.onButtonPermLock)
    self.ui.find('btn-info').connect(gui.CLICK, self.onButtonInfo)

    # todo: it would be most excellent if, when showscreen was false
    #       (i.e.  the screen is blanked), that the `click` would turn
    #       the screen on, but nothing further...
    self.ui.connect(gui.CLICK, self.onButtonClick)

    self.state.on('showscreen:changed', self.onShowScreen)
    self.state.showscreen = True

  #----------------------------------------------------------------------------
  def onButtonClick(self):
    self.wake()

  #----------------------------------------------------------------------------
  def onButtonAlert(self):    print 'CLICKED: btn-alert'
  def onButtonWeather(self):  print 'CLICKED: btn-weather'
  def onButtonExit(self):     print 'CLICKED: btn-exit'

  #----------------------------------------------------------------------------
  def onButtonUnlock(self):
    print 'CLICKED: btn-unlock'
    self.lock.state = 0

  #----------------------------------------------------------------------------
  def onButtonLock(self):
    print 'CLICKED: btn-lock'
    self.lock.state = self.lock.LOCKED

  #----------------------------------------------------------------------------
  def onButtonPermLock(self):
    print 'CLICKED: btn-permlock'
    self.lock.state = self.lock.LOCKED | self.lock.PERMANENT

  #----------------------------------------------------------------------------
  def onButtonInfo(self):
    print 'CLICKED: btn-info'

  # #----------------------------------------------------------------------------
  # def initCamera(self):
  #   if self.options.mock:
  #     self.camera   = camera.MockCamera()
  #   else:
  #     self.camera   = picamera.PiCamera()
  #     atexit.register(self.camera.close)
  #   self.camera.resolution     = (240, 180)
  #   self.camera.crop           = (0.0, 0.0, 1.0, 1.0)
  #   self.camera.image_effect   = 'none'
  #   self.camera.ISO            = 0
  #   self.camthread             = CameraCaptureThread(self)
  #   self.camthread.daemon = True
  #   self.camthread.start()

  #----------------------------------------------------------------------------
  def initLock(self):
    self.lock = \
        lock.MockLock() \
        if self.options.mock else \
        lock.RaspiLock()
    self.lock.change.subscribe(self.lockChanged)
    self.lock.state = self.lock.LOCKED

  #----------------------------------------------------------------------------
  def lockChanged(self, *args, **kw):
    msg = _('N/A')
    if self.lock.tostate is not None:
      if self.lock.tostate & self.lock.LOCKED:
        msg = _('Locking...')
      else:
        msg = _('Unlocking...')
    else:
      if self.lock.state & self.lock.LOCKED:
        if self.lock.state & self.lock.PERMANENT:
          msg = _('PERMA-\nLOCKED')
        else:
          msg = _('LOCKED')
      else:
        msg = _('UNLOCKED')
    self.ui.infobox.find('lbl-lock-state').set_text(msg)
    # todo: notify of redraw needed...
    # TODO: modify lock buttons to be slightly transparent if "active"...

  #----------------------------------------------------------------------------
  def getNextService(self):
    nexts = [svc.next for svc in self.services if svc.next is not None]
    if nexts:
      return min(nexts)
    return None

  #----------------------------------------------------------------------------
  def mainLoop(self):
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    # pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
    # pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
    pygame.event.set_blocked(pygame.KEYDOWN)
    # todo: what *are* pygame.ACTIVEEVENT?...
    # pygame.event.set_blocked(pygame.ACTIVEEVENT)

    self.redraw()

    nsvc = self.getNextService()

    while True:

      # NOTE: i hate the way events are handled in this application...
      #       *BUT* there are several problems in the pygame ecosystem:
      #         - pygame.event.wait() relies on SDL_WaitEvent
      #           ... but SDL_WaitEvent doesn't wait; it polls. wtf.
      #         - pygame.fastevent.wait() does not rely on SDL_WaitEvent
      #           ... but it has a 10ms timer that polls to see if
      #               SDL has posted any events. wtf.
      #         - there does not seem to be any way of asking SDL to
      #           notify us of an event without polling. wtf.

      event = pygame.event.poll()

      # handle UI events
      if event and event.type != pygame.NOEVENT:
        self.handle(event)

      # give services a chance to make a difference
      cur = time.time()
      if cur >= nsvc:
        for svc in self.services:
          if svc.next is not None and svc.next <= cur:
            svc.run()
        nsvc = self.getNextService()

      # TODO: i need to *NOT* do this for every tick...
      self.redraw()

      # sleep for some period of time
      # TODO: if the screen is "on" sleep for 0.1, else longer...
      sleep = 0.1
      if nsvc is not None:
        sleep = max(0.001, min(sleep, nsvc - time.time()))
      time.sleep(sleep)

  #----------------------------------------------------------------------------
  def handle(self, event):

    if event.type == CaptureEvent.id:
      captures = pygame.event.get(CaptureEvent.id)
      if captures:
        print '[--] WARNING: DROPPING %d FRAMES...' % (len(captures),)
        event = captures[-1]
      self.displayCapture(event.image)
      return

    # if event.type == pygame.MOUSEBUTTONUP:
    #   pos = pygame.mouse.get_pos()
    #   for btn in self.buttons.values():
    #     if btn.selected(pos):
    #       break
    #   continue

    if event.type == pygame.QUIT \
        or ( event.type == pygame.KEYUP \
             and event.key == pygame.K_ESCAPE and not event.mod ):
      # TODO: display `working` image...
      log.info('exit requested - quitting...')
      pygame.quit()
      raise SystemExit()

    print 'EVENT:',repr(event)
    self.pguapp.event(event)

  #----------------------------------------------------------------------------
  def redraw(self):
    self.screen.fill(0)
    if self.state.showscreen:
      self.pguapp.paint()
    pygame.display.update()

  # #----------------------------------------------------------------------------
  # def displayCapture(self, image):
  #   self.screen.blit(image, (0, 0))
  #   pygame.display.update()

  # #----------------------------------------------------------------------------
  # def toggleInfo(self):
  #   self.camthread.running = not self.state.showcam
  #   self.infolbl.visible   = self.state.showcam
  #   if self.state.showcam:
  #     self.infolbl.draw(self.screen)
  #     # todo: restrict update to only label area...
  #     pygame.display.update()
  #   self.state.showcam = not self.state.showcam

  # #----------------------------------------------------------------------------
  # def onShowCamera(self, old, new):
  #   self.buttons['info'].icon = 'icon-action-info' if new else 'icon-action-cam'
  #   self.buttons['info'].draw(self.screen)
  #   # todo: restrict update to only button area...
  #   pygame.display.update()

  # # #----------------------------------------------------------------------------
  # # def displayCapture(self, stream):
  # #   if not self.dispimg.Shown:
  # #     return
  # #   # TODO: check to see if we are falling behind and, if so, drop the frame
  # #   # TODO: apparently, converting the stream to bitmap must be done in the
  # #   #       main gui thread (otherwise i get XInitThreads complaints...).
  # #   #       that sucks. figure out how to move this into a separate thread.
  # #   bitmap = wx.BitmapFromImage(wx.ImageFromStream(stream))
  # #   self.dispimg.SetBitmap(bitmap)
    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

#   #----------------------------------------------------------------------------
#   def start(self):
#     self.MainLoop()

#   #----------------------------------------------------------------------------
#   def OnInit(self):
#     # todo: convert to using pkg_resources...
#     #         self.wxres = wx.xrc.EmptyXmlResource()
#     #         self.wxres.LoadFromString( ...load... )
#     #       *but*... how does loading of images, etc work?
#     # todo: degrade to known locale if selected locale does not exist...
#     self.wxres = wx.xrc.XmlResource(
#       os.path.join(
#         os.path.dirname(__file__), 'res', 'wx.%s.xrc' % (self.options.locale,)))
#     self.main = self.wxres.LoadFrame(None, 'MainFrame')
#     if self.options.geometry:
#       self.main.SetSize(self.options.geometry)
#     else:
#       self.main.ShowFullScreen(True)
#     self.main.Show()
#     self.SetTopWindow(self.main)
#     self.initDisplay()
#     self.initReminder()
#     self.initTime()
#     self.initWeather()
#     self.initButtons()
#     self.lockChanged()
#     return True

#   #----------------------------------------------------------------------------
#   def initDisplay(self):
#     self.disppanel = wx.xrc.XRCCTRL(self.main, 'DisplayPanel')
#     self.disptext  = wx.xrc.XRCCTRL(self.main, 'DisplayText')
#     self.dispimg   = wx.xrc.XRCCTRL(self.main, 'DisplayImage')
#     self.lock.change.subscribe(self.lockChanged)
#     self.disp_thread = CameraCaptureThread(self)
#     self.disp_thread.daemon = True
#     self.disp_thread.start()

#   #----------------------------------------------------------------------------
#   def displayCapture(self, stream):
#     if not self.dispimg.Shown:
#       return
#     # TODO: check to see if we are falling behind and, if so, drop the frame
#     # TODO: apparently, converting the stream to bitmap must be done in the
#     #       main gui thread (otherwise i get XInitThreads complaints...).
#     #       that sucks. figure out how to move this into a separate thread.
#     bitmap = wx.BitmapFromImage(wx.ImageFromStream(stream))
#     self.dispimg.SetBitmap(bitmap)

#   #----------------------------------------------------------------------------
#   def toggleDisplay(self, event):
#     self.showDisplayCamera(self.disptext.Shown)

#   #----------------------------------------------------------------------------
#   def initReminder(self):
#     # TODO
#     self.rembox = wx.xrc.XRCCTRL(self.main, 'ReminderText')
#     self.rembox.SetLabel('to 10:30PM: max/rakesh for dinner')

#   #----------------------------------------------------------------------------
#   def initTime(self):
#     # TODO
#     self.timebox = wx.xrc.XRCCTRL(self.main, 'NowTimeText')
#     self.timebox.SetLabel('9:35 pm')

#   #----------------------------------------------------------------------------
#   def initWeather(self):
#     # TODO
#     self.ntempbox = wx.xrc.XRCCTRL(self.main, 'NowTempText')
#     self.ntempbox.SetLabel('23°C')
#     self.ntempbox = wx.xrc.XRCCTRL(self.main, 'TodayTempText')
#     self.ntempbox.SetLabel('25°/17°C')

#   #----------------------------------------------------------------------------
#   def initButtons(self):
#     # TODO
#     self.btnleave   = wx.xrc.XRCCTRL(self.main, 'LeaveButton')
#     self.btnunlock  = wx.xrc.XRCCTRL(self.main, 'UnlockButton')
#     self.btnlock    = wx.xrc.XRCCTRL(self.main, 'LockButton')
#     self.btnplock   = wx.xrc.XRCCTRL(self.main, 'PermlockButton')
#     self.btninfo    = wx.xrc.XRCCTRL(self.main, 'InfoButton')

#     self.btnleave.Bind(wx.EVT_LEFT_UP, self.do_leave)
#     self.btnunlock.Bind(wx.EVT_LEFT_UP, self.do_unlock)
#     self.btnlock.Bind(wx.EVT_LEFT_UP, self.do_lock)
#     self.btnplock.Bind(wx.EVT_LEFT_UP, self.do_plock)
#     self.btninfo.Bind(wx.EVT_LEFT_UP, self.toggleDisplay)

#   #----------------------------------------------------------------------------
#   def showDisplayCamera(self, show):
#     self.disp_thread.running = show
#     # TODO: set/cancel timers for showing camera vs. text, etc...
#     self.disptext.Show(not show)
#     self.dispimg.Show(show)

#   #----------------------------------------------------------------------------
#   def do_leave(self, event):
#     self.lock.state = self.lock.ONCLOSE

#   #----------------------------------------------------------------------------
#   def do_unlock(self, event):
#     self.lock.state = 0

#   #----------------------------------------------------------------------------
#   def do_lock(self, event):
#     self.lock.state = self.lock.LOCKED

#   #----------------------------------------------------------------------------
#   def do_plock(self, event):
#     self.lock.state = self.lock.LOCKED | self.lock.PERMANENT

#   #----------------------------------------------------------------------------
#   def lockChanged(self, **kw):
#     msg = _('N/A')

#     # self.btnleave.SetTransparent(150)
#     # self.btnunlock.SetTransparent(150)
#     # self.btnlock.SetTransparent(150)
#     # self.btnplock.SetTransparent(150)

#     if self.lock.tostate is not None:
#       # TODO: what about self.lock.ONCLOSE ?...
#       # todo: what about transparency?...
#       if self.lock.tostate & self.lock.LOCKED:
#         msg = _('Locking...')
#       else:
#         msg = _('Unlocking...')
#     else:
#       # todo: what about transparency on self.lock.ONCLOSE?...
#       if self.lock.state & self.lock.LOCKED:
#         if self.lock.state & self.lock.PERMANENT:
#           msg = _('PERMA-\nLOCKED')
#           # self.btnplock.SetTransparent(255)
#         else:
#           msg = _('LOCKED')
#           # self.btnlock.SetTransparent(255)
#       else:
#         msg = _('UNLOCKED')
#         # self.btnunlock.SetTransparent(255)
#     self.disptext.SetLabel(msg)
#     self.showDisplayCamera(False)
#     self.disppanel.Layout()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
