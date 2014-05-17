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
import wx, wx.xrc
from aadict import aadict
import morph
import six
import threading
import time

from .i18n import _
from . import lock, camera

#------------------------------------------------------------------------------
class CameraCaptureThread(threading.Thread):

  # #----------------------------------------------------------------------------
  # class CaptureEvent(wx.PyEvent):
  #   ID = wx.NewId()
  #   def __init__(self, bitmap):
  #     wx.PyEvent.__init__(self)
  #     self.SetEventType(self.ID)
  #     self.bitmap = bitmap

  #----------------------------------------------------------------------------
  def __init__(self, app, fps=10, *args, **kw):
    super(CameraCaptureThread, self).__init__(*args, **kw)
    self.app      = app
    self._running = False
    self._cond    = threading.Condition()
    self._timeout = 1.0 / float(self.app.getConfig('camera.fps', 10))
    self._buf     = six.BytesIO()

  #----------------------------------------------------------------------------
  @property
  def running(self):
    with self._cond:
      return self._running
  @running.setter
  def running(self, value):
    with self._cond:
      self._running = value
      self._cond.notify()

  #----------------------------------------------------------------------------
  def run(self):
    while True:
      with self._cond:
        if not self._running:
          self._cond.wait()
          continue
        self.capture()
        self._cond.wait(self._timeout)

  #----------------------------------------------------------------------------
  def capture(self):
    # todo: make this `resize` depend on the screen...
    self._buf.seek(0)
    self.app.camera.capture(self._buf, format='png', resize=(240, 180))
    self._buf.seek(0)
    bmp = wx.BitmapFromImage(wx.ImageFromStream(self._buf))
    # wx.PostEvent(self.app.dispimg, CameraCaptureThread.CaptureEvent(bmp))
    wx.CallAfter(self.app.onCapture, aadict(bitmap=bmp))

#------------------------------------------------------------------------------
class App(wx.App):

  #----------------------------------------------------------------------------
  def __init__(self, options, *args, **kw):
    self.options = aadict(vars(options))
    # process options
    self.options.geometry = self.options.geometry or 'fullscreen'
    if self.options.geometry == 'fullscreen':
      self.options.geometry = None
    else:
      self.options.geometry = tuple(
        [int(e) for e in self.options.geometry.split('x')])
    self.options.mock   = morph.tobool(self.options.mock)
    self.options.locale = self.options.locale or 'en'
    # start resources
    # todo: check & use self.options.remote...
    self.lock    = lock.MockLock() if self.options.mock else lock.RaspiLock()
    self.camera  = camera.MockCamera() if self.options.mock else camera.RaspiCamera() # todo
    self.weather = None # todo
    super(App, self).__init__(*args, **kw)

  #----------------------------------------------------------------------------
  def start(self):
    self.MainLoop()

  #----------------------------------------------------------------------------
  def getConfig(self, option, default=None, section='gui'):
    try:
      return self.options.config.get(section, option)
    except Exception as err:
      return default

  #----------------------------------------------------------------------------
  def OnInit(self):
    # todo: convert to using pkg_resources...
    #         self.wxres = wx.xrc.EmptyXmlResource()
    #         self.wxres.LoadFromString( ...load... )
    #       *but*... how does loading of images, etc work?
    # todo: degrade to known locale if selected locale does not exist...
    self.wxres = wx.xrc.XmlResource(
      os.path.join(
        os.path.dirname(__file__), 'res', 'wx.%s.xrc' % (self.options.locale,)))
    self.main = self.wxres.LoadFrame(None, 'MainFrame')
    if self.options.geometry:
      self.main.SetSize(self.options.geometry)
    else:
      self.main.ShowFullScreen(True)
    self.main.Show()
    self.SetTopWindow(self.main)
    self.initDisplay()
    self.initReminder()
    self.initTime()
    self.initWeather()
    self.initButtons()
    self.lockChanged()
    return True

  #----------------------------------------------------------------------------
  def initDisplay(self):
    self.disppanel = wx.xrc.XRCCTRL(self.main, 'DisplayPanel')
    self.disptext  = wx.xrc.XRCCTRL(self.main, 'DisplayText')
    self.dispimg   = wx.xrc.XRCCTRL(self.main, 'DisplayImage')
    self.lock.change.subscribe(self.lockChanged)
    self.disp_thread = CameraCaptureThread(self)
    self.disp_thread.daemon = True
    self.disp_thread.start()
    # self.dispimg.Connect(-1, -1, CameraCaptureThread.CaptureEvent.ID, self.onCapture)

  #----------------------------------------------------------------------------
  def onCapture(self, event):
    # todo: perhaps check to make sure that the camera is visible?
    # TODO: check to see if we are falling behind and, if so, drop the frame
    self.dispimg.SetBitmap(event.bitmap)

  #----------------------------------------------------------------------------
  def toggleDisplay(self, event):
    self.showDisplayCamera(self.disptext.Shown)

  #----------------------------------------------------------------------------
  def initReminder(self):
    # TODO
    self.rembox = wx.xrc.XRCCTRL(self.main, 'ReminderText')
    self.rembox.SetLabel('to 10:30PM: max/rakesh for dinner')

  #----------------------------------------------------------------------------
  def initTime(self):
    # TODO
    self.timebox = wx.xrc.XRCCTRL(self.main, 'NowTimeText')
    self.timebox.SetLabel('9:35 pm')

  #----------------------------------------------------------------------------
  def initWeather(self):
    # TODO
    self.ntempbox = wx.xrc.XRCCTRL(self.main, 'NowTempText')
    self.ntempbox.SetLabel('23°C')
    self.ntempbox = wx.xrc.XRCCTRL(self.main, 'TodayTempText')
    self.ntempbox.SetLabel('25°/17°C')

  #----------------------------------------------------------------------------
  def initButtons(self):
    # TODO
    self.btnleave   = wx.xrc.XRCCTRL(self.main, 'LeaveButton')
    self.btnunlock  = wx.xrc.XRCCTRL(self.main, 'UnlockButton')
    self.btnlock    = wx.xrc.XRCCTRL(self.main, 'LockButton')
    self.btnplock   = wx.xrc.XRCCTRL(self.main, 'PermlockButton')
    self.btninfo    = wx.xrc.XRCCTRL(self.main, 'InfoButton')

    self.btnleave.Bind(wx.EVT_LEFT_UP, self.do_leave)
    self.btnunlock.Bind(wx.EVT_LEFT_UP, self.do_unlock)
    self.btnlock.Bind(wx.EVT_LEFT_UP, self.do_lock)
    self.btnplock.Bind(wx.EVT_LEFT_UP, self.do_plock)
    self.btninfo.Bind(wx.EVT_LEFT_UP, self.toggleDisplay)

  #----------------------------------------------------------------------------
  def showDisplayCamera(self, show):
    self.disp_thread.running = show
    # TODO: set/cancel timers for showing camera vs. text, etc...
    self.disptext.Show(not show)
    self.dispimg.Show(show)

  #----------------------------------------------------------------------------
  def do_leave(self, event):
    self.lock.state = self.lock.ONCLOSE

  #----------------------------------------------------------------------------
  def do_unlock(self, event):
    self.lock.state = 0

  #----------------------------------------------------------------------------
  def do_lock(self, event):
    self.lock.state = self.lock.LOCKED

  #----------------------------------------------------------------------------
  def do_plock(self, event):
    self.lock.state = self.lock.LOCKED | self.lock.PERMANENT

  #----------------------------------------------------------------------------
  def lockChanged(self, **kw):
    msg = _('N/A')

    # self.btnleave.SetTransparent(150)
    # self.btnunlock.SetTransparent(150)
    # self.btnlock.SetTransparent(150)
    # self.btnplock.SetTransparent(150)

    if self.lock.tostate is not None:
      # TODO: what about self.lock.ONCLOSE ?...
      # todo: what about transparency?...
      if self.lock.tostate & self.lock.LOCKED:
        msg = _('Locking...')
      else:
        msg = _('Unlocking...')
    else:
      # todo: what about transparency on self.lock.ONCLOSE?...
      if self.lock.state & self.lock.LOCKED:
        if self.lock.state & self.lock.PERMANENT:
          msg = _('PERMA-\nLOCKED')
          # self.btnplock.SetTransparent(255)
        else:
          msg = _('LOCKED')
          # self.btnlock.SetTransparent(255)
      else:
        msg = _('UNLOCKED')
        # self.btnunlock.SetTransparent(255)
    self.disptext.SetLabel(msg)
    self.showDisplayCamera(False)
    self.disppanel.Layout()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
