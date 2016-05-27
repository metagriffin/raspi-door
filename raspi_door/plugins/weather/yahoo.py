# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2014/06/08
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

import requests
import asset
from aadict import aadict
from xml.etree import ElementTree as ET

#------------------------------------------------------------------------------
@asset.plugin('raspi_door.plugins.weather', 'yahoo', final=True)
class YahooWeather(object):

  # documentation for weather api service:
  #   https://developer.yahoo.com/weather/

  DEFAULT_URL           = 'http://weather.yahooapis.com/forecastrss'
  DEFAULT_WOEID         = '615702'

  METRIC                = 'metric'
  IMPERIAL              = 'imperial'

  namespaces  = dict(
    yweather    = 'http://xml.weather.yahoo.com/ns/rss/1.0',
    geo         = 'http://www.w3.org/2003/01/geo/wgs84_pos#',
  )

  #----------------------------------------------------------------------------
  def __init__(self, service, *args, **kw):
    super(YahooWeather, self).__init__(*args, **kw)
    self.service  = service
    self.url      = self.service.getConfig('url', self.DEFAULT_URL)
    self.units    = self.service.getConfig('units', self.METRIC)
    if self.units not in (self.METRIC, self.IMPERIAL):
      raise ValueError('"units" must be one of metric, kelvin, or imperial')
    self.woeid    = self.service.getConfig('location.id', self.DEFAULT_WOEID)

  #----------------------------------------------------------------------------
  def fetch(self):

    # todo: do some error recovery!...
    # todo: do better image caching...

    req = requests.get(self.url, timeout=10, params={
      'w' : self.woeid,
      'u' : 'c' if self.units == self.METRIC else 'f'
    })
    req.raise_for_status()
    ns  = self.namespaces
    doc = ET.fromstring(req.content)
    data = aadict(build=doc.find('./channel/lastBuildDate', namespaces=ns).text)
    for attr in ('location', 'units', 'wind', 'atmosphere', 'astronomy', 'condition'):
      data[attr] = aadict(doc.find('.//yweather:' + attr, namespaces=ns).attrib)
    data.location = aadict(
      id    = self.woeid,
      text  = ', '.join([data.location[e] for e in ('city', 'region', 'country') if data.location[e]]),
      lat   = float(doc.find('.//geo:lat', namespaces=ns).text),
      lon   = float(doc.find('.//geo:long', namespaces=ns).text))
    data.forecast = [
      aadict(node.attrib)
      for node in doc.findall('.//yweather:forecast', namespaces=ns)]
    desc = '<root>' + doc.find('.//item/description', namespaces=ns).text + '</root>'
    data.image_url = ET.fromstring(desc).find('.//img').attrib['src']

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

    return data

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
