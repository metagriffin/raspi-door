# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/05/16
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

import asset

#------------------------------------------------------------------------------
class MockCamera(object):

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    self.current = 0

  #----------------------------------------------------------------------------
  def capture(self, output, format=None, use_video_port=False, resize=None, splitter_port=0, **options):
    if format is not 'png':
      raise ValueError('MockPiCamera only supports format "png"')
    if resize != (240, 180):
      raise ValueError('MockPiCamera only supports resize to 240x180')
    output.write(asset.load('raspi_door:res/mock/camera-%d.png' % (self.current,)).read())
    self.current = ( self.current + 1 ) % 8

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
