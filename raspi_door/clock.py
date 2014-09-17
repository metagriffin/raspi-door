# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/06/08
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

import time
import pytz
from datetime import datetime

from .service import Service

#------------------------------------------------------------------------------
class ClockService(Service):

  section = 'clock'

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(ClockService, self).__init__(*args, **kw)

  #----------------------------------------------------------------------------
  def start(self):
    self.format   = self.getConfig('format', '%H:%M')
    # todo: to make this interval test a little more resilient, it
    #       should render a given time (such as 8:43:33) as well as
    #       one second later -- if they differ, then it needs seconds.
    self.interval = 1 if '%s' in self.format.lower() else 60
    self.tz       = pytz.timezone(self.getConfig('tz', 'US/Eastern'))
    return self.bumpNext()

  #----------------------------------------------------------------------------
  def bumpNext(self):
    if self.next is not None:
      cur = time.time()
      while self.next < cur:
        self.next += self.interval
      return self
    # set initial time; note: the next will be set in the *past* in
    # order to force this to be called very soon...
    cur = self.tz.localize(datetime.now()).replace(microsecond=0)
    if self.interval == 1:
      self.next = int(time.mktime(cur.timetuple()))
    elif self.interval == 60:
      self.next = int(time.mktime(cur.replace(second=0).timetuple()))
    else:
      raise ValueError('`ClockService.interval` currently only supports 1 or 60')
    return self

  #----------------------------------------------------------------------------
  def run(self):
    # todo: is this really the right way???
    txt = pytz.utc.localize(datetime.utcfromtimestamp(time.time())) \
      .astimezone(self.tz).strftime(self.format)
    widget = self.app.ui.find('lbl-clock')
    widget.set_text(txt)
    return self.bumpNext()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
