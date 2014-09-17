# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/05/09
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

import threading
import smoke
#import wx

# todo: convert Lock into a LockService?...

#------------------------------------------------------------------------------
class Lock(smoke.Broker):

  LOCKED     = 1 << 0
  PERMANENT  = 1 << 1

  change        = smoke.signal('change')
  stateChange   = smoke.signal('state-change')
  tostateChange = smoke.signal('tostate-change')
  requestChange = smoke.signal('request-change')

  #----------------------------------------------------------------------------
  def __init__(self, state=0):
    self._state   = state
    self._tostate = None
    self._request = None
    self._rlock   = threading.RLock()

  #----------------------------------------------------------------------------
  @property
  def state(self):
    return self._state
  @state.setter
  def state(self, value):
    self.request = value

  #----------------------------------------------------------------------------
  @property
  def tostate(self):
    return self._tostate
  @tostate.setter
  def tostate(self, value):
    self.request = value

  #----------------------------------------------------------------------------
  @property
  def request(self):
    return self._request
  @request.setter
  def request(self, value):
    if value == self._request \
        or ( self._request is None and value == self._tostate ) \
        or ( self._request is None and self._tostate is None and value == self._state ):
      return
    with self._rlock:
      self._update('request', value)
      self._process()

  #----------------------------------------------------------------------------
  def _update(self, attr, value):
    oldval = getattr(self, '_' + attr)
    if oldval == value:
      return
    setattr(self, '_' + attr, value)
    self._trigger(attr, old=oldval, value=value)

  #----------------------------------------------------------------------------
  def _trigger(self, attr, **kw):
    self.change.publish(attribute=attr, **kw)
    self.publish(attr + '-change', attribute=attr, **kw)

  #----------------------------------------------------------------------------
  def _process(self):
    raise NotImplementedError()

#------------------------------------------------------------------------------
class RaspiLock(Lock):
  # TODO: implement...
  pass

#------------------------------------------------------------------------------
class MockLock(Lock):

  #----------------------------------------------------------------------------
  def _process(self):
    if self._request is None:
      return
    if self._tostate is not None:
      return
    self._update('tostate', self._request)
    self._update('request', None)
    self._defer(1, self.process_next)

  #----------------------------------------------------------------------------
  def process_next(self):
    with self._rlock:
      if self._tostate is None:
        return
      self._update('state', self._tostate)
      self._update('tostate', self._request)
      self._update('request', None)
      if self._tostate is not None:
        self._defer(1, self.process_next)

  #----------------------------------------------------------------------------
  def _defer(self, seconds, func, *args, **kw):
    t = threading.Timer(seconds, func, *args, **kw)
    t.daemon = True
    t.start()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
