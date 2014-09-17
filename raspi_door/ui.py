# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/05/29
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

from pgu import gui

from .sizer import Sizer
from .button import IconButton

#------------------------------------------------------------------------------
class UI(gui.Container):

  #----------------------------------------------------------------------------
  def __init__(self, app, *args, **kw):
    super(UI, self).__init__(*args, **kw)
    self.app = app
    self.populate()

  #----------------------------------------------------------------------------
  def populate(self):

    self.box = Sizer(width=self.rect.w, height=self.rect.h)

    self.alertbox = Sizer(orient=Sizer.HORIZONTAL) \
        .add(IconButton('icon-action-message', name='btn-alert')) \
        .add(gui.Label('--', cls='label.alert', name='lbl-alert'),
             weight=1, flags=Sizer.EXPAND)

    self.infobox = Sizer(width=240, height=180) \
        .add(gui.Label('--', cls='label.huge', name='lbl-lock-state'), weight=132, flags=Sizer.EXPAND) \
        .add(self.alertbox, weight=48, flags=Sizer.EXPAND)

    self.weatherbox = Sizer(orient=Sizer.HORIZONTAL) \
        .add(Sizer() \
               .add(gui.Label('--', cls='label.big', name='lbl-now-temp'), weight=1, flags=Sizer.EXPAND) \
               .add(gui.Label('--:--', cls='label.big', name='lbl-clock'), weight=1, flags=Sizer.EXPAND),
             weight=1, flags=Sizer.EXPAND) \
        .add(IconButton('weather-na', name='btn-weather')) \
        .add(Sizer() \
               .add(gui.Label('--/--', name='lbl-forecast-temp'), weight=1, flags=Sizer.EXPAND) \
               .add(gui.Label('--', name='lbl-now-text'), weight=1, flags=Sizer.EXPAND) \
               .add(gui.Label('--', name='lbl-now-wind'), weight=1, flags=Sizer.EXPAND),
             weight=1, flags=Sizer.EXPAND)

    self.btnbox = Sizer(orient=Sizer.HORIZONTAL) \
        .add(IconButton('icon-action-exit', name='btn-exit').setStyle('hidden', True), weight=1) \
        .add(IconButton('icon-action-unlock', name='btn-unlock'), weight=1) \
        .add(IconButton('icon-action-lock', name='btn-lock'), weight=1) \
        .add(IconButton('icon-action-permlock', name='btn-permlock').setStyle('hidden', True), weight=1) \
        .add(IconButton('icon-action-cam', name='btn-info'), weight=1)

    self.box.add(self.infobox, flags=Sizer.EXPAND)
    self.box.add(self.weatherbox, weight=48, flags=Sizer.EXPAND)
    self.box.add(self.btnbox, weight=48, flags=Sizer.EXPAND)

    self.add(self.box, 0, 0)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
