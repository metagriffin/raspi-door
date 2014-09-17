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

import pygame
from pgu import gui
import morph

#------------------------------------------------------------------------------
def isHidden(w):
  return getattr(w.style, 'hidden', False)

#------------------------------------------------------------------------------
class Sizer(gui.Container):

  '''
  A simple flow-oriented container that allows sub-widgets to be sized
  based on relative weight.

  IMPORTANT: although very similar to wx.Sizer in functionality, it is
  different in the following very significant way: a wx.Sizer is not
  an actual widget, it is merely a layout helper, whereas this Sizer
  is an an actual widget that behaves as a container. This is "less
  than ideal" in the traditional GUI approach, however, it works well
  in the domain of lightweight implementations that pygame and pgu
  live in. As a result of this, you *must*, at a minimum, provide the
  Sizer with `width` and `height` attributes...
  '''

  #: `orient` constants
  VERTICAL   = 0
  HORIZONTAL = 1

  #: `align` constants
  TOP        = 1
  RIGHT      = 2
  BOTTOM     = 4
  LEFT       = 8

  #: `flags` constants
  EXPAND     = 1
  NOSCALE    = 2

  #----------------------------------------------------------------------------
  class Axis(object):
    def __init__(self, horiz):
      self.pos   = 'x'           if horiz else 'y'
      self.size  = 'w'           if horiz else 'h'
      self.bef   = Sizer.LEFT    if horiz else Sizer.TOP
      self.aft   = Sizer.RIGHT   if horiz else Sizer.BOTTOM

  #----------------------------------------------------------------------------
  def __init__(self, orient=VERTICAL, *args, **kw):
    kw.setdefault('cls', 'sizer')
    super(Sizer, self).__init__(*args, **kw)
    self._factors = {}
    self.horiz    = orient == self.HORIZONTAL
    self.major    = Sizer.Axis(self.horiz)
    self.minor    = Sizer.Axis(not self.horiz)
    self.debug    = self.style.debug
    if self.debug:
      self.debug = pygame.Color(self.debug)

  #----------------------------------------------------------------------------
  @property
  def visible_widgets(self):
    return [w for w in self.widgets if not isHidden(w)]

  #----------------------------------------------------------------------------
  def add(self, widget, weight=None, align=0, flags=0):
    super(Sizer, self).add(widget, 0, 0)
    self._factors[id(widget)] = [weight, align, flags]
    return self

  #----------------------------------------------------------------------------
  def resize(self, width=None, height=None):
    # style.x, style.y, style.width, style.height, style.align, style.valign
    # rect.x, rect.y, rect.w, rect.h
    if isHidden(self):
      return (0, 0)
    if width is not None:
      self.style.width = width
    if height is not None:
      self.style.height = height
    width  = self.style.width
    height = self.style.height
    majdim = width        if self.horiz else height
    majpos = self.style.x if self.horiz else self.style.y
    mindim = height       if self.horiz else width
    minpos = self.style.y if self.horiz else self.style.x
    # first, determine available space
    tweight, tspace = 0.0, majdim
    for w in self.widgets:
      if isHidden(w):
        w.resize()
        w.rect.x = w.rect.y = w.rect.w = w.rect.h = 10
        continue
      spec = self._factors[id(w)]
      if spec[0] is None:
        w.rect.w, w.rect.h = w.resize()
        tspace  -= getattr(w.rect, self.major.size)
      else:
        tweight += spec[0]
    assert tspace >= 0, 'fixed widgets exceeded allocatable Sizer space'
    # allocate available space & align widgets
    cpos  = 0
    crect = [None, None]
    for w in self.visible_widgets:
      spec = self._factors[id(w)]
      csize = getattr(w.rect, self.major.size)
      if spec[0] is not None:
        csize = tspace * spec[0] / tweight
      if spec[2] & self.EXPAND:
        crect[0] = csize  if self.horiz else width
        crect[1] = height if self.horiz else csize
      else:
        crect = [None, None]
      w.rect.w, w.rect.h = w.resize(*crect)
      if spec[2] & self.EXPAND:
        # todo: what if these sizes are *smaller* than the resize() sizes?...
        #       ==> check NOSCALE. and reuse the scaling code in the `else`...
        setattr(w.rect, self.major.pos, cpos)
        setattr(w.style, self.major.pos, cpos)
        setattr(w.rect, self.major.size, csize)
        setattr(w.style, self.major.size, csize)
        setattr(w.rect, self.minor.pos, 0)
        setattr(w.style, self.minor.pos, 0)
        setattr(w.rect, self.minor.size, mindim)
        setattr(w.style, self.minor.size, mindim)
      else:
        coffset = csize - getattr(w.rect, self.major.size)
        soffset = mindim - getattr(w.rect, self.minor.size)
        if coffset < 0 or soffset < 0:
          if spec[2] & self.NOSCALE:
            if coffset < 0:
              raise AttributeError('widget is too large for sizer (in major axis)')
            if soffset < 0:
              raise AttributeError('widget is too large for sizer (in minor axis)')
          scale = min(float(csize) / getattr(w.rect, self.major.size),
                      float(mindim) / getattr(w.rect, self.minor.size))
          w.rect.w, w.rect.h = w.resize(int(round(scale * w.rect.w)), int(round(scale * w.rect.h)))
          coffset = csize - getattr(w.rect, self.major.size)
          soffset = mindim - getattr(w.rect, self.minor.size)
        if spec[1] & self.major.bef and not spec[1] & self.major.aft:
          coffset = cpos
        elif not spec[1] & self.major.bef and spec[1] & self.major.aft:
          coffset = cpos + coffset
        else:
          coffset = cpos + ( coffset / 2 )
        setattr(w.rect, self.major.pos, coffset)
        setattr(w.style, self.major.pos, coffset)
        if spec[1] & self.minor.bef and not spec[1] & self.minor.aft:
          soffset = 0
        elif not spec[1] & self.minor.bef and spec[1] & self.minor.aft:
          soffset = soffset
        else:
          soffset = soffset / 2
        setattr(w.rect, self.minor.pos, soffset)
        setattr(w.style, self.minor.pos, soffset)
      cpos += csize
    return (width, height)

  #----------------------------------------------------------------------------
  def paint(self, surface):
    if isHidden(self):
      return (0, 0)
    ret = super(Sizer, self).paint(surface)
    if not self.debug:
      return ret
    bc = self.debug
    for wdgt in self.visible_widgets:
      x, y, w, h = wdgt.rect.x, wdgt.rect.y, wdgt.rect.w - 1, wdgt.rect.h - 1
      pygame.draw.line(surface, bc, (x, y), (x + w, y))
      pygame.draw.line(surface, bc, (x + w, y), (x + w, y + h))
      pygame.draw.line(surface, bc, (x + w, y + h), (x, y + h))
      pygame.draw.line(surface, bc, (x, y + h), (x, y))
    return ret

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
