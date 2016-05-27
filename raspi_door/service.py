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
from datetime import datetime

import morph
import pytz

#------------------------------------------------------------------------------
class Service(object):

  section = 'DEFAULT'

  DEFAULT_TZ            = 'UTC'
  DEFAULT_LOCALE        = 'en'

  #----------------------------------------------------------------------------
  def __init__(self, app, *args, **kw):
    super(Service, self).__init__(*args, **kw)
    self.app    = app
    self.next   = None
    self.mock   = morph.tobool(self.getConfig('mock', 'false'))
    self.tz     = pytz.timezone(self.getConfig('tz', self.DEFAULT_TZ))
    self.locale = self.getConfig('locale', self.DEFAULT_LOCALE)

  #----------------------------------------------------------------------------
  def getConfig(self, option, default=None, **kw):
    kw.setdefault('section', self.section)
    return self.app.getConfig(option, default, **kw)

  #----------------------------------------------------------------------------
  def ts2dt(self, epoch):
    '''
    Converts unix epoch timestamp `epoch` to a timezone-aware
    datetime.datetime object using the timezone specified for
    this service.
    '''
    return datetime.fromtimestamp(epoch, self.tz)

  #----------------------------------------------------------------------------
  def dt2ts(self, dt):
    # TODO: if dt is "timezone-naive", assume in `self.tz`
    return (dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

  #----------------------------------------------------------------------------
  def ts2str(self, fmt=None, epoch=None):
    if epoch is None:
      if fmt is not None and isinstance(fmt, (int, float)):
        fmt, epoch = None, fmt
      else:
        epoch = time.time()
    if not fmt:
      fmt = 'iso-8601-combined'
    if fmt.lower() in ('iso', 'iso-8601', 'iso-8601-combined'):
      ms = '.%03d' % (round(epoch * 1000) % 1000,)
      return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(epoch)) + ms + 'Z'
    return time.strftime(fmt, self.ts2dt(epoch).timetuple())

  #----------------------------------------------------------------------------
  def start(self):
    return self

  #----------------------------------------------------------------------------
  def run(self):
    raise NotImplementedError()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
