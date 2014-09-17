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
import argparse
import logging
import six
from six.moves import configparser as CP

from .app import App
from .i18n import _

#------------------------------------------------------------------------------
def main(args=None):

  cli = argparse.ArgumentParser(
    description = _('Raspberry Pi smart-ish door controller.'),
  )

  cli.add_argument(
    _('-v'), _('--verbose'),
    dest='verbose', action='count',
    default=int(os.environ.get('RASPIDOOR_VERBOSE', '0')),
    help=_('increase logging verbosity (can be specified multiple times)'))

  cli.add_argument(
    _('-c'), _('--config'), metavar=_('FILENAME'),
    dest='configPath',
    default=os.environ.get('RASPIDOOR_CONFIG', '~/.config/raspi-door/config.ini'),
    help=_('configuration filename (current default: "{}")', '%(default)s'))

  cli.add_argument(
    _('-g'), _('--geometry'), metavar=_('GEOMETRY'),
    dest='geometry',
    help=_('set the window geometry (either WIDTHxHEIGHT or "fullscreen")'))

  cli.add_argument(
    _('-m'), _('--mock'),
    dest='mock', default=False, action='store_true',
    help=_('don\'t attempt to connect to any hardware'))

  # cli.add_argument(
  #   _('-r'), _('--remote'),
  #   dest='remote', default=None, action='store',
  #   help=_('specify remote raspi-door-server URL'))

  options = cli.parse_args(args=args)

  # TODO: send logging to "log" window?...
  rootlog = logging.getLogger()
  rootlog.setLevel(logging.WARNING)
  rootlog.addHandler(logging.StreamHandler())
  # TODO: add a logging formatter...
  # TODO: configure logging from config.ini?... ==> `[gui] verbose = X`
  if options.verbose == 1:
    rootlog.setLevel(logging.INFO)
  elif options.verbose > 1:
    rootlog.setLevel(logging.DEBUG)

  options.configPath = os.path.expanduser(os.path.expandvars(options.configPath))

  cfg = options.config = CP.SafeConfigParser()
  cfg.read(options.configPath)

  # todo: there has *got* to be a better way of merging options...
  if cfg.has_section('gui'):
    if cfg.has_option('gui', 'verbose'):
      options.verbose = max(options.verbose, cfg.getint('gui', 'verbose'))
    for opt in cfg.options('gui'):
      if opt in ('verbose',):
        continue
      if not getattr(options, opt, None):
        val = cfg.get('gui', opt)
        setattr(options, opt, val)

  App(options).start()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
