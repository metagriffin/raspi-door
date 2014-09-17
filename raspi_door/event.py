# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/05/20
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

import pygame
import threading
import time

_curidx = 0

#------------------------------------------------------------------------------
def newEvent():
  # TODO: make this threadsafe...
  global _curidx
  _curidx += 1
  eid = pygame.USEREVENT + _curidx
  def makeEvent(*args, **kw):
    return pygame.event.Event(eid, *args, **kw)
  makeEvent.id = eid
  return makeEvent

# #------------------------------------------------------------------------------
# class _Scheduler(object):

#   #----------------------------------------------------------------------------
#   def __init__(self, *args, **kw):
#     super(_Scheduler, self).__init__(*args, **kw)
#     self._cond    = threading.Condition()

#   #----------------------------------------------------------------------------
#   def defer(time, callback, *args, **kw):
#     pass


#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
