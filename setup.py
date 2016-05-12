#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/05/13
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

import os, sys, setuptools
from setuptools import setup, find_packages

# require python 2.7+
if sys.hexversion < 0x02070000:
  raise RuntimeError('This package requires python 2.7 or better')

heredir = os.path.abspath(os.path.dirname(__file__))
def read(*parts, **kw):
  try:    return open(os.path.join(heredir, *parts)).read()
  except: return kw.get('default', '')

test_dependencies = [
  'nose                 >= 1.3.0',
  'coverage             >= 3.5.3',
]

dependencies = [
  'smoke                >= 0.2.0',
  'picamera             >= 0.8',
  'RPi.GPIO             >= 0.5.5',
  'six                  >= 1.8.0',
  'aadict               >= 0.2.2',
  'morph                >= 0.1.2',
  'asset                >= 0.6.10',          # globre >= 0.0.5
  'pygame               >= 1.9.1',
  'pgu                  >= 0.18',
  'pytz                 >= 2014.4',
  'requests             >= 2.3.0',
  'protobuf             >= 2.5.0',
]

entrypoints = {
  'console_scripts': [
    'raspi-door         = raspi_door:main',
  ],
}

classifiers = [
  'Development Status :: 2 - Pre-Alpha',
  #'Development Status :: 3 - Alpha',
  #'Development Status :: 4 - Beta',
  #'Development Status :: 5 - Production/Stable',
  'Environment :: X11 Applications',
  'Environment :: Win32 (MS Windows)',
  'Environment :: MacOS X',
  'Environment :: Other Environment',
  'Natural Language :: English',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Intended Audience :: End Users/Desktop',
  'Topic :: Home Automation',
  'Topic :: Utilities',
  'Topic :: Security',
  'Topic :: Multimedia :: Video :: Capture',
  'Topic :: Scientific/Engineering :: Image Recognition',
  'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
]

setup(
  name                  = 'raspi_door',
  version               = read('VERSION.txt', default='0.0.1').strip(),
  description           = 'Raspberry Pi Smart-ish Door',
  long_description      = read('README.rst'),
  classifiers           = classifiers,
  author                = 'metagriffin',
  author_email          = 'mg.pypi@metagriffin.net',
  url                   = 'http://github.com/metagriffin/raspi-door',
  keywords              = 'raspberry pi door smart-ish automation recognition gui',
  packages              = find_packages(),
  platforms             = ['any'],
  include_package_data  = True,
  zip_safe              = False, # todo: get pgu.gui.Theme to use pkg_resources...
  install_requires      = dependencies,
  tests_require         = test_dependencies,
  test_suite            = 'raspi_door',
  entry_points          = entrypoints,
  license               = 'GPLv3+',
)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
