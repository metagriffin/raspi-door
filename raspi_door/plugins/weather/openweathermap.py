# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2016/05/12
# copy: (C) Copyright 2016-EOT metagriffin -- see LICENSE.txt
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
import re

import requests
import asset
from aadict import aadict

from ...util import parsedur

#------------------------------------------------------------------------------
# MONKEY-PATCH!
# todo: remove this if/when this PR is accepted:
#   https://github.com/kennethreitz/requests/pull/1894
if not hasattr(requests.Response, 'require_ok'):
  def require_ok(self):
    self.raise_for_status()
    return self
  requests.Response.require_ok = require_ok
# /MONKEY-PATCH!
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
@asset.plugin('raspi_door.plugins.weather', 'openweathermap', final=True)
class OpenWeatherMap(object):

  DEFAULT_URL           = 'http://api.openweathermap.org/data/2.5'
  DEFAULT_APIKEY        = '0186ee1de078533203fc459fd05e3eed'

  METRIC                = 'metric'
  KELVIN                = 'kelvin'
  IMPERIAL              = 'imperial'

  #----------------------------------------------------------------------------
  def __init__(self, service, *args, **kw):
    super(OpenWeatherMap, self).__init__(*args, **kw)
    self.service  = service
    self.url      = self.service.getConfig('url', self.DEFAULT_URL)
    self.units    = self.service.getConfig('units', self.METRIC)
    if self.units not in (self.METRIC, self.KELVIN, self.IMPERIAL):
      raise ValueError('"units" must be one of metric, kelvin, or imperial')

  #----------------------------------------------------------------------------
  def fetch(self):
    params = dict(
      appid  = self.service.getConfig('apikey', self.DEFAULT_APIKEY),
      units  = self.units,
      mode   = 'json',
    )
    if self.service.getConfig('location.id'):
      params['id'] = self.service.getConfig('location.id')
    else:
      params['q'] = self.service.getConfig('location', 'Paris, FR')

    ret = aadict.d2ar(
      requests.get(self.url + '/weather', params=params).require_ok().json())

    # TODO: make all of these time.ctime and time.strftime use `tz` instead!

    ret.units = aadict(
      temperature = {'kelvin': 'K', 'metric': 'C', 'imperial': 'F'}[self.units],
      pressure    = 'hPa',
      speed       = {'kelvin': 'm/s', 'metric': 'm/s', 'imperial': 'mi/h'}[self.units],
      distance    = 'N/A',  # todo: does OWM have this?
    )
    ret.build = time.ctime(ret.dt)
    ret.location = aadict(
      id          = ret.id,
      text        = ret.name,
      lat         = str(ret.coord.lat),
      lon         = str(ret.coord.lon),
    )
    ret.condition = aadict(
      date        = ret.build,
      text        = ret.weather[0].description.capitalize(),  # todo: if too long, use weather[0].main
      code        = ret.weather[0].id,
      icon        = ret.weather[0].icon,
      temp        = str(int(round(ret.main.temp))),
    )
    ret.image_url = 'http://openweathermap.org/img/w/{}.png'.format(ret.weather[0].icon)
    ret.wind.direction = str(ret.wind.deg)
    ret.wind.chill = ret.condition.temp  # todo: does OWM really not have a wind-chill???
    ret.atmosphere = aadict(
      pressure    = str(ret.main.pressure),
      rising      = 'N/A',  # todo: does OWM have this?
      visibility  = 'N/A',  # todo: does OWM have this?
      humidity    = str(ret.main.humidity),
    )
    ret.astronomy = aadict(
      sunrise     = re.sub('^0', '', time.strftime('%I:%M %p', time.localtime(ret.sys.sunrise)).lower()),
      sunset      = re.sub('^0', '', time.strftime('%I:%M %p', time.localtime(ret.sys.sunset)).lower()),
    )

    ret.forecast = []

    params  = dict(
      appid   = self.service.getConfig('apikey', self.DEFAULT_APIKEY),
      units   = self.units,
      mode    = 'json',
      id      = ret.location.id,
    )

    res     = aadict.d2ar(
      requests.get(self.url + '/forecast', params=params).require_ok().json())

    offset  = parsedur(self.service.getConfig('forecast.today.offset', '6h'))
    cutoff  = parsedur(self.service.getConfig('forecast.today.cutoff', '21h'))
    nowts   = time.time()
    nowdt   = self.service.ts2dt(nowts)
    todaydt = nowdt.replace(hour=0, minute=0, second=0, microsecond=0)
    todayts = self.service.dt2ts(todaydt)

    if nowts + offset < todayts + cutoff:
      print 'forecast: today'
      target  = nowts + offset
      istoday = True
    else:
      print 'FORECAST: TOMORROW'
      # todo: should the tomorrow's forecast time be configurable?
      target  = todayts + ( 1.5 * 86400 )
      istoday = False

    # TODO: make this get the "noon" values for the forecasts...
    # TODO: use config "tomorrow" to determine the *next* value...
    #       and then make an "offset" like value for the next value, eg "+6h"
    #       ==> remember that this must be tz-aware...

    for item in sorted(res.list, key=lambda i: i.dt):
      if not ret.forecast:
        if item.dt < target:
          continue
      else:
        if item.dt < ( ret.forecast[-1].dt + 86400 ):
          continue
      ret.forecast.append(aadict(
        dt     = item.dt,
        temp   = str(int(round(item.main.temp))),
        high   = str(int(round(item.main.temp_max))),
        low    = str(int(round(item.main.temp_min))),
        code   = item.weather[0].id,
        icon   = item.weather[0].icon,
        text   = item.weather[0].description.capitalize(),  # todo: if too long, use weather[0].main
        date   = re.sub('^0', '', time.strftime('%d %b %Y', time.localtime(item.dt))),
        day    = time.strftime('%a', time.localtime(item.dt)),
        today  = False,
      ))
      if len(ret.forecast) == 1 and istoday:
        ret.forecast[0].today = True
        ret.forecast[0].day = re.sub(
          '^0', '', time.strftime('%I%p', time.localtime(item.dt))).lower()

    # data = {
    #   'build': 'Sun, 08 Jun 2014 11:49 am EDT',
    #   'units': {'distance':'km','speed':'km/h','temperature':'C','pressure':'mb'},
    #   'location': {'id': '2459115', 'text': 'New York, NY, United States', 'lat': 40.67, 'lon': -73.95},
    #   'condition': {'date':'Sun, 08 Jun 2014 11:49 am EDT','text':'Fair','code':'34','temp':'28'},
    #   'image_url':'http://l.yimg.com/a/i/us/we/52/34.gif',
    #   'wind': {'direction':'0','speed':'0','chill':'28'},
    #   'atmosphere': {'pressure':'1014','rising':'2','visibility':'16.09','humidity':'35'},
    #   'astronomy': {'sunset':'8:23 pm','sunrise':'5:23 am'},
    #   'forecast':
    #   [
    #     {'high':'27','code':'45','low':'18','date':'8 Jun 2014','text':'Showers Late','day':'Sun'},
    #     {'high':'21','code':'12','low':'18','date':'9 Jun 2014','text':'Rain/Thunder','day':'Mon'},
    #     {'high':'27','code':'11','low':'19','date':'10 Jun 2014','text':'Showers','day':'Tue'},
    #     {'high':'24','code':'26','low':'18','date':'11 Jun 2014','text':'Cloudy','day':'Wed'},
    #     {'high':'23','code':'26','low':'19','date':'12 Jun 2014','text':'Cloudy','day':'Thu'},
    #   ],
    # }

    return ret


#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
