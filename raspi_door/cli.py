# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/05/07
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

import os
# import os.path
import argparse
import logging
# import wx
# import wx.lib.embeddedimage
# from wx.lib.wordwrap import wordwrap
# from wx import xrc, wizard
# from secpass import engine, api
# import asset
# import morph
# import six
# from six.moves import configparser as CP

#from . import taskbar
from .app import App
from .i18n import _

#------------------------------------------------------------------------------
def main(args=None):

  cli = argparse.ArgumentParser(
    description = _('Raspberry Pi intelligent door GUI.'),
  )

  cli.add_argument(
    _('-v'), _('--verbose'),
    dest='verbose', action='count',
    default=int(os.environ.get('RASPIDOOR_VERBOSE', '0')),
    help=_('increase logging verbosity (can be specified multiple times)'))

  cli.add_argument(
    _('-c'), _('--config'), metavar=_('FILENAME'),
    dest='config',
    default=os.environ.get('RASPIDOOR_CONFIG', '~/.config/raspi-door/config.ini'),
    help=_('configuration filename (current default: "{}")', '%(default)s'))

  cli.add_argument(
    _('-m'), _('--mock'),
    dest='mock', default=False, action='store_true',
    help=_('don\'t attempt to connect to any hardware'))

  cli.add_argument(
    _('-r'), _('--remote'),
    dest='remote', default=None, action='store',
    help=_('specify remote raspi-door-server URL'))

  options = cli.parse_args(args=args)

  # todo: share this with secpass?...
  # TODO: send logging to "log" window?... (is this done by wx???)
  rootlog = logging.getLogger()
  rootlog.setLevel(logging.WARNING)
  rootlog.addHandler(logging.StreamHandler())
  # TODO: add a logging formatter...
  # TODO: configure logging from config.ini?...
  if options.verbose == 1:
    rootlog.setLevel(logging.INFO)
  elif options.verbose > 1:
    rootlog.setLevel(logging.DEBUG)

  options.config = os.path.expanduser(os.path.expandvars(options.config))

  App(options).start()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
