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

# shamelessly adapted from:
#   https://github.com/adafruit/adafruit-pi-cam/blob/master/cam.py

import six
import asset
import pygame
import morph

RESDIR = 'raspi_door:res/image'

#------------------------------------------------------------------------------
class Icon(object):

  _cache = dict()

  #----------------------------------------------------------------------------
  def __init__(self, name, stream=None):
    self.name   = name
    if stream is None:
      stream = six.BytesIO(asset.load(RESDIR + '/' + self.name + '.png').read())
    self.bitmap = pygame.image.load(stream)

  #----------------------------------------------------------------------------
  @staticmethod
  def load(name):
    if not morph.isstr(name):
      return Icon('<stream>', stream=name)
    if name not in Icon._cache:
      Icon._cache[name] = Icon(name)
    return Icon._cache[name]

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
