# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/05/27
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

'''
A pitiful python port of Backbone.Event...
'''

import logging
import traceback

#------------------------------------------------------------------------------
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class Trap(object):

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(Trap, self).__init__(*args, **kw)
    self._listeners = []

  #----------------------------------------------------------------------------
  def on(self, event, callback):
    attr = None
    if ':' in event:
      attr, event = event.split(':', 1)
    self._listeners.append((attr or None, event, callback))

  #----------------------------------------------------------------------------
  def off(self, event=None, callback=None):
    raise NotImplementedError('Trap.off()')

  #----------------------------------------------------------------------------
  def trigger(self, topic, event, *args, **kw):
    for target in self._listeners:
      if target[0] and target[0] != topic:
        continue
      if target[1] and target[1] != event:
        continue
      try:
        target[2](*args, topic=topic, event=event, **kw)
      except Exception as err:
        log.exception('error while triggering trap event')

#------------------------------------------------------------------------------
class AttributeTrap(Trap):

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(AttributeTrap, self).__init__(*args, **kw)

  #----------------------------------------------------------------------------
  def __getattr__(self, name):
    return self.__dict__.get(name, None)

  #----------------------------------------------------------------------------
  def __setattr__(self, name, value):
    if name in ('_listeners',):
      self.__dict__[name] = value
      return
    if name not in self.__dict__:
      self.trigger(name, 'init', value=value)
    old = self.__dict__.get(name, None)
    if old == value:
      return
    self.__dict__[name] = value
    self.trigger(name, 'changed', old=old, new=value)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
