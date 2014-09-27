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

import six
import asset
import pygame

#------------------------------------------------------------------------------
class ICamera(object):
  def capture(self, output, *args, **kw):
    raise NotImplementedError()

#------------------------------------------------------------------------------
class MockCamera(ICamera):

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    self.current = 0

  #----------------------------------------------------------------------------
  def capture(self, output, format=None, use_video_port=False, resize=None, splitter_port=0, **options):
    if format is not 'png':
      raise ValueError('MockCamera only supports format "png"')
    data = asset.load('raspi_door:res/mock/camera-%d.png' % (self.current,)).read()
    ret = None
    if resize is None:
      output.write(data)
    else:
      buf = six.BytesIO(data)
      img = pygame.image.load(buf)
      if True:
      # if img.get_size() == resize:
      #   output.write(data)
      # else:
        img = pygame.transform.scale(img, resize)
        # todo: submit a patch to pygame to support a 'format=format' param...
        pygame.image.save(img, output)
        ret = pygame.image.tostring(img, 'RGB')
    self.current = ( self.current + 1 ) % 8
    return ret

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
