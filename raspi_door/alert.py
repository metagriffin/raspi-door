# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/09/16
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
import logging
import morph

from .service import Service
from .icon import Icon

#------------------------------------------------------------------------------
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class AlertService(Service):

  section = 'alert'

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(AlertService, self).__init__(*args, **kw)
    # todo: move `mock` into `service.Service`...
    self.mock = morph.tobool(self.getConfig('mock', 'false'))
    self.showing = False

    if not self.mock:
      raise NotImplementedError('AlertService: only `mock` mode is implemented')

  #----------------------------------------------------------------------------
  def start(self):
    return self.bumpNext()

  #----------------------------------------------------------------------------
  def bumpNext(self):
    if self.next is None:
      self.next = time.time()
      return self
    self.next = time.time() + ( 0.2 if self.showing else 1 )
    return self

  #----------------------------------------------------------------------------
  def run(self):
    self.app.ui.alertbox.find('lbl-alert').set_text(self.getConfig('message', '[NoMessage]'))
    # TODO: make this work (i think it may be a Sizer issue...)
    #       ==> it is causing an AssertionError in:
    #         pgu/gui/surface.py, line 16:
    #           assert(r.w >= 0 and r.h >= 0)
    # self.app.ui.alertbox.style.hidden = self.showing
    if not self.showing:
      self.app.ui.alertbox.find('lbl-alert').set_text('')
      self.app.ui.alertbox.find('btn-alert').style.hidden = True
    else:
      self.app.ui.alertbox.find('btn-alert').style.hidden = False
    self.showing = not self.showing
    return self.bumpNext()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
