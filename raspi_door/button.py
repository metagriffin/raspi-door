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

import pygame
from pgu import gui
import morph

from .icon import Icon

#------------------------------------------------------------------------------
class IconButton(gui.Button):

  #----------------------------------------------------------------------------
  def __init__(self, icon, *args, **kw):
    kw.setdefault('cls', 'iconbutton')
    if morph.isstr(icon):
      icon = gui.Image(Icon.load(icon).bitmap)
    if not isinstance(icon, gui.Image):
      raise ValueError('IconButton only works with pgu.gui.Image objects')
    super(IconButton, self).__init__(icon, *args, **kw)

  #----------------------------------------------------------------------------
  def resize(self, width, height):
    # todo: handle the case where one but not both of width & height are None
    if width is not None and height is not None \
        and self.value.value.get_size() != (width, height):
      newicon = pygame.transform.scale(self.value.value, (width, height))
      self.value = gui.Image(newicon)
    return super(IconButton, self).resize(width, height)

  #----------------------------------------------------------------------------
  def setStyle(self, param, value):
    setattr(self.style, param, value)
    return self

  #----------------------------------------------------------------------------
  def __repr__(self):
    if self.name:
      return '<IconButton "%s">' % self.name
    return '<IconButton object at 0x%s>' % (id(self),)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
