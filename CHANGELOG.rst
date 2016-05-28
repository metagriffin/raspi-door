=========
ChangeLog
=========


v0.7.1
======

* Fixed handling of null wind chill factor


v0.7.0
======

* Fixed weather service to properly use the `tz` configuration

* Added OpenWeatherMap.org configurations to control tomorrow's
  forecast:

  * forecast.tomorrow.offset

* Re-added the "yahoo" weather service driver (though it appears to be
  non-functional without authentication) -- buyer beware

* Added startup sound "Ready to serve!"

* Other small fix-ups and clean-ups


v0.6.1
======

* Added OpenWeatherMap.org configurations to control which
  forecast timeframe is displayed:

  * forecast.today.offset
  * forecast.today.cutoff


v0.5.0
======

* Moved to use OpenWeatherMap.org for weather data


v0.4.0
======

* Add sample configuration output
* Cleaned up non-Raspberry Pi run/mock mode


v0.3.0
======

* Made sensors work properly for non-mock GPIO mode


v0.2.0
======

* First tagged release
