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

from .i18n import _
from . import lock

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
    self.camera  = None # todo
    self.weather = None # todo
    super(App, self).__init__(*args, **kw)

  #----------------------------------------------------------------------------
  def start(self):
    self.MainLoop()

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

  #----------------------------------------------------------------------------
  def initTime(self):
    # TODO
    self.timebox = wx.xrc.XRCCTRL(self.main, 'NowTimeText')
    self.timebox.SetLabel('9:35')

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
    self.btninfo.Bind(wx.EVT_LEFT_UP, self.toggleInfo)

  #----------------------------------------------------------------------------
  def toggleInfo(self, event):
    self.showDisplayText(not self.disptext.Shown)

  #----------------------------------------------------------------------------
  def showDisplayText(self, show):
    # self.disptext.SetHidden(not self.disptext.IsHidden())
    # self.dispimg.SetHidden(not self.dispimg.IsHidden())
    if show:
      # TODO: cancel timer
      self.disptext.Show()
      self.dispimg.Hide()
    else:
      # TODO: set timer to return to text...
      self.disptext.Hide()
      self.dispimg.Show()

  #----------------------------------------------------------------------------
  def toggleLock(self, event):
    print 'togglelock'
    # TODO: replace this with:
    #         def do_lock(self, event):
    #           self.lock.state = self.lock.LOCKED
    if self.lock.state & self.lock.LOCKED:
      self.lock.state &= ~ self.lock.LOCKED
    else:
      self.lock.state |= self.lock.LOCKED

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
    if self.lock.tostate is not None:
      # TODO: what about self.lock.ONCLOSE ?...
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
    self.disptext.SetLabel(msg)
    self.showDisplayText(True)
    self.disppanel.Layout()


#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
