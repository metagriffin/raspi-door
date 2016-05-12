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

import os
import time
import threading
import logging
import csv

from aadict import aadict
from pgu import gui
import six
import asset

from .service import Service
from .icon import Icon
from .util import parsedur

#------------------------------------------------------------------------------
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class WeatherService(Service):

  section     = 'weather'

  DEFAULT_DRIVER        = 'openweathermap'

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    super(WeatherService, self).__init__(*args, **kw)
    self.data = aadict()

  #----------------------------------------------------------------------------
  def start(self):
    self.interval = parsedur(self.getConfig('interval', '30m'))
    self.thread = threading.Thread(
      name='raspi_door.weather.WeatherService', target=self.runBackground)
    self.driver = asset.plugins('raspi_door.plugins.weather').select(
      self.getConfig('driver', self.DEFAULT_DRIVER)).handle(self)
    self.thread.daemon = True
    self.thread.start()
    return self.bumpNext()

  #----------------------------------------------------------------------------
  def bumpNext(self):
    self.next = time.time() + 1
    if self.data.pending or self.data.last is None:
      return self
    if self.mock:
      self.next = time.time() + ( self.interval / 3.0 )
      return self
    self.next = max(self.next, self.data.last + self.interval)
    return self

  # data = {
  #   'build': 'Sun, 08 Jun 2014 11:49 am EDT',
  #   'units': {'distance':'km','speed':'km/h','temperature':'C','pressure':'mb'},
  #   'location': {'id': '2459115', 'text': 'New York, NY, United States', 'lat': 40.67, 'lon': -73.95}
  #   'condition': {'date':'Sun, 08 Jun 2014 11:49 am EDT','text':'Fair','code':'34','temp':'28'}
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

  #----------------------------------------------------------------------------
  def run(self):
    if not self.data.last:
      return self.bumpNext()
    if ( time.time() - self.data.last ) >= ( 2 * self.interval ):
      # probably having issues...
      self.app.ui.weatherbox.find('lbl-forecast-temp').set_text('--/--')
      self.app.ui.weatherbox.find('lbl-now-temp').set_text('--')
      self.app.ui.weatherbox.find('lbl-now-text').set_text('--')
      self.app.ui.weatherbox.find('lbl-now-wind').set_text('--')
      self.app.ui.weatherbox.find('btn-weather').value = gui.Image(Icon.load('weather-na').bitmap)
      return self.bumpNext()
    forecast = self.data.forecast[0]
    deg = u'°'
    self.app.ui.weatherbox.find('lbl-forecast-temp').set_text(
      forecast.day + ': ' + forecast.high + deg + '/' + forecast.low + deg)
    # todo: change this to make it a % probability of rain, if rain...
    self.app.ui.weatherbox.find('lbl-now-text').set_text(self.data.condition.text)
    wspeed = float(self.data.wind.speed)
    wunit  = self.data.units.speed
    if wunit == 'm/s':
      # m/s => km/h
      wunit = 'km/h'
      wspeed = wspeed * 3.600
    wspeed = int(round(wspeed))
    if not wspeed:
      self.app.ui.weatherbox.find('lbl-now-wind').set_text('No wind')
    else:
      self.app.ui.weatherbox.find('lbl-now-wind').set_text(
        str(wspeed)
        + ' ' + wunit
        + ' ' + self.deg2dir(float(self.data.wind.direction)))
    self.app.ui.weatherbox.find('lbl-now-temp').set_text(
      self.data.wind.chill + deg + self.data.units.temperature)
    icname = self.cond2icname(self.data.condition.icon)
    self.app.ui.weatherbox.find('btn-weather').value = \
      gui.Image(Icon.load(icname).bitmap)
    # todo: if the icon is unknown, perhaps download the yahoo image?...
    # self.data.image = requests.get(self.data.image_url).content
    # self.app.ui.weatherbox.find('btn-weather').value = \
    #   gui.Image(Icon.load(six.BytesIO(self.data.image)).bitmap)
    return self.bumpNext()

  #----------------------------------------------------------------------------
  conditions = {

    # TODO: convert this to use the OWM weather "id" instead of the icon...
    #       (lots more specificity...)

    None    : ('weather-na',                         'Not available'), # not using yahoo icon!...
    # ICON : ( ICON-NAME, DOCUMENTATION-NAME )
    '01d'   : ('yahoo-clear-d',                      'clear sky (day)' ),
    '01n'   : ('yahoo-clear-n',                      'clear sky (night)' ),
    '02d'   : ('yahoo-fair-d',                       'few clouds (day)' ),
    '02n'   : ('yahoo-fair-n',                       'few clouds (night)' ),
    '03d'   : ('yahoo-partly-cloudy-d',              'scattered clouds (day)' ),
    '03n'   : ('yahoo-partly-cloudy-n',              'scattered clouds (night)' ),
    '04d'   : ('yahoo-mostly-cloudy-d',              'broken clouds (day)' ),
    '04n'   : ('yahoo-mostly-cloudy-n',              'broken clouds (night)' ),
    '09d'   : ('yahoo-showers',                      'shower rain (day)' ),
    '09n'   : ('yahoo-showers',                      'shower rain (night)' ),
    '10d'   : ('yahoo-scattered-showers',            'rain (day)' ),
    '10n'   : ('yahoo-scattered-showers',            'rain (night)' ),
    '11d'   : ('yahoo-thunderstorms',                'thunderstorm (day)' ),
    '11n'   : ('yahoo-scattered-thunderstorms-n',    'thunderstorm (night)' ),
    '13d'   : ('yahoo-snow',                         'snow (day)' ),
    '13n'   : ('yahoo-snow',                         'snow (night)' ),
    '50d'   : ('yahoo-foggy',                        'mist (day)' ),
    '50n'   : ('yahoo-foggy',                        'mist (night)' ),

    # # CODE  : ( ICON-NAME,                           DOCUMENTATION-NAME )
    # '0'     : ('yahoo-tornado',                      'Tornado'),
    # '1'     : ('yahoo-tropical-storm',               'Tropical storm'),
    # '2'     : ('yahoo-hurricane',                    'Hurricane'),
    # '3'     : ('yahoo-severe-thunderstorms',         'Severe thunderstorms'),
    # '4'     : ('yahoo-thunderstorms',                'Thunderstorms'),
    # '5'     : ('yahoo-rain-and-snow',                'Mixed rain and snow'),
    # '6'     : ('yahoo-rain-and-sleet',               'Mixed rain and sleet'),
    # '7'     : ('yahoo-snow-and-sleet',               'Mixed snow and sleet'),
    # '8'     : ('yahoo-freezing-drizzle',             'Freezing drizzle'),
    # '9'     : ('yahoo-drizzle',                      'Drizzle'),
    # '10'    : ('yahoo-freezing-rain',                'Freezing rain'),
    # '11'    : ('yahoo-showers',                      'Showers'), # note: same as 12?
    # '12'    : ('yahoo-showers',                      'Showers'), # note: same as 11?
    # '13'    : ('yahoo-snow-flurries',                'Snow flurries'),
    # '14'    : ('yahoo-light-snow-showers',           'Light snow showers'),
    # '15'    : ('yahoo-blowing-snow',                 'Blowing snow'),
    # '16'    : ('yahoo-snow',                         'Snow'),
    # '17'    : ('yahoo-hail',                         'Hail'),
    # '18'    : ('yahoo-sleet',                        'Sleet'),
    # '19'    : ('yahoo-dust',                         'Dust'),
    # '20'    : ('yahoo-foggy',                        'Foggy'),
    # '21'    : ('yahoo-haze',                         'Haze'),
    # '22'    : ('yahoo-smoky',                        'Smoky'),
    # '23'    : ('yahoo-blustery',                     'Blustery'),
    # '24'    : ('yahoo-windy',                        'Windy'),
    # '25'    : ('weather-cold',                       'Cold'), # not using yahoo icon!...
    # '26'    : ('yahoo-cloudy',                       'Cloudy'),
    # '27'    : ('yahoo-mostly-cloudy-n',              'Mostly cloudy (night)'),
    # '28'    : ('yahoo-mostly-cloudy-d',              'Mostly cloudy (day)'),
    # '29'    : ('yahoo-partly-cloudy-n',              'Partly cloudy (night)'),
    # '30'    : ('yahoo-partly-cloudy-d',              'Partly cloudy (day)'),
    # '31'    : ('yahoo-clear-n',                      'Clear (night)'),
    # '32'    : ('yahoo-sunny',                        'Sunny'),
    # '33'    : ('yahoo-fair-n',                       'Fair (night)'),
    # '34'    : ('yahoo-fair-d',                       'Fair (day)'),
    # '35'    : ('yahoo-rain-and-hail',                'Mixed rain and hail'),
    # '36'    : ('weather-hot',                        'Hot'), # not using yahoo icon!...
    # '37'    : ('yahoo-isolated-thunderstorms',       'Isolated thunderstorms'),
    # '38'    : ('yahoo-scattered-thunderstorms-n',    'Scattered thunderstorms'), # note: same as 39?
    # '39'    : ('yahoo-scattered-thunderstorms-d',    'Scattered thunderstorms'), # note: same as 38?
    # '40'    : ('yahoo-scattered-showers',            'Scattered showers'),
    # '41'    : ('yahoo-heavy-snow',                   'Heavy snow'), # note: same as 43?
    # '42'    : ('yahoo-scattered-snow-showers',       'Scattered snow showers'),
    # '43'    : ('yahoo-heavy-snow',                   'Heavy snow'), # note: same as 41?
    # '44'    : ('yahoo-partly-cloudy',                'Partly cloudy'),
    # '45'    : ('yahoo-thundershowers',               'Thundershowers'),
    # '46'    : ('yahoo-snow-showers',                 'Snow showers'),
    # '47'    : ('yahoo-isolated-thundershowers',      'Isolated thundershowers'),

  }
  def cond2icname(self, code):
    code = str(code)
    if code not in self.conditions:
      return self.conditions[None][0]
    return self.conditions[code][0]

  #----------------------------------------------------------------------------
  directions = (
    'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', )
  def deg2dir(self, deg):
    tot = 360.0
    siz = tot / len(self.directions)
    return self.directions[int(round(deg / siz)) % len(self.directions)]

  #----------------------------------------------------------------------------
  def setData(self, data):

    self.data.pending = False
    if data is None:
      return self
    data = aadict.d2ar(data)

    # TODO: this is yucky... strip this down to the "bare necessities"...
    if self.getConfig('csvlog'):
      fname = self.getConfig('csvlog')
      header = not os.path.exists(fname)
      with open(fname, 'ab') as fp:
        csvw = csv.writer(fp, quoting=csv.QUOTE_MINIMAL)
        if header:
          csvw.writerow([
            'timestamp', 'build',
            'units.distance', 'units.speed', 'units.temperature', 'units.pressure',
            'location.id', 'location.text', 'location.lat', 'location.lon',
            'current.code', 'current.temperature', 'current.text', 'current.time', 'current.image',
            'wind.speed', 'wind.direction', 'wind.chill',
            'atmosphere.pressure', 'atmosphere.rising', 'atmosphere.visibility', 'atmosphere.humidity',
            'astronomy.sunrise', 'astronomy.sunset',
            'forecast.date', 'forecast.day', 'forecast.code', 'forecast.high', 'forecast.low', 'forecast.text',
          ])
        csvw.writerow([
          time.time(), data.build,
          data.units.distance, data.units.speed, data.units.temperature, data.units.pressure,
          data.location.id, data.location.text, data.location.lat, data.location.lon,
          data.condition.code, data.condition.temp, data.condition.text, data.condition.date, data.image_url,
          data.wind.speed, data.wind.direction, data.wind.chill,
          data.atmosphere.pressure, data.atmosphere.rising, data.atmosphere.visibility, data.atmosphere.humidity,
          data.astronomy.sunrise, data.astronomy.sunset,
          data.forecast[0].date, data.forecast[0].day, data.forecast[0].code, data.forecast[0].high, data.forecast[0].low, data.forecast[0].text,
        ])

    self.data.update(**data)
    self.data.last = time.time()
    return self

  #----------------------------------------------------------------------------
  def runBackground(self):
    while True:
      try:
        self.data.pending = True
        self.setData(self.fetch())
        time.sleep(self.interval)
      except Exception:
        log.exception('error while update weather state')
        self.setData(None)
        time.sleep(10)

  #----------------------------------------------------------------------------
  def fetch(self):
    if self.mock:
      return self.mockFetch()
    return self.driver.fetch()

  #----------------------------------------------------------------------------
  def mockFetch(self):
    time.sleep(0.25)
    if self.mock is True:
      self.mock = aadict(cond=0, dir=0)
    else:
      self.mock.cond = ( self.mock.cond + 1 ) % len(self.conditions)
      self.mock.dir  = ( self.mock.dir + 1 ) % len(self.directions)
    cond = sorted([int(k) for k in self.conditions.keys()])
    cond = str(cond[self.mock.cond % len(cond)])
    fcast = {
      'high' : str(len(self.conditions)),
      'code' : cond,
      'low'  : str(len(self.directions)),
      'date' : '8 Jun 2014',
      'text' : self.conditions[cond][1],
      'day'  : 'Mok',
    }
    data = {
      'build': 'Sun, 08 Jun 2014 11:49 am EDT',
      'units': {'distance':'km','speed':'km/h','temperature':'C','pressure':'mb'},
      'location': {'id': '2459115', 'text': 'New York, NY, United States', 'lat': 40.67, 'lon': -73.95},
      'condition': {
        'date': 'Sun, 08 Jun 2014 11:49 am EDT',
        'text': self.conditions[cond][1],
        'code': cond,
        'temp': cond,
      },
      'image_url':'http://l.yimg.com/a/i/us/we/52/34.gif',
      'wind': {
        'direction' : str( 360.0 / len(self.directions) * self.mock.dir ),
        'speed'     : str( 360.0 / len(self.directions) * self.mock.dir ),
        'chill'     : cond,
      },
      'atmosphere': {'pressure':'1014','rising':'2','visibility':'16.09','humidity':'35'},
      'astronomy': {'sunset':'8:23 pm','sunrise':'5:23 am'},
      'forecast': [fcast, fcast, fcast, fcast, fcast],
    }
    return data

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
