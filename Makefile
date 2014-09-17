PKGNAME = raspi_door
include Makefile.python

yahoo-svg:
	./bin/yahoo-weather-css-parser.py \
	  raspi_door/res/yahoo-weather-conditions-svg.css \
	  raspi_door/res/svg

yahoo-png:
	for svgname in `ls -1 raspi_door/res/svg/yahoo-*.svg` ; do \
	  fname=`echo "$$svgname" | sed -re 's:.*svg/(.*)\.svg$$:\1:'` ; \
	  echo "[  ] converting $$fname..." ; \
	  inkscape --without-gui --export-width=48 \
	    "$$svgname" --export-png="raspi_door/res/image/$$fname.png" ; \
	done

weather-png:
	for svgname in `ls -1 raspi_door/res/svg/weather-*.svg` ; do \
	  fname=`echo "$$svgname" | sed -re 's:.*svg/(.*)\.svg$$:\1:'` ; \
	  echo "[  ] converting $$fname..." ; \
	  inkscape --without-gui --export-width=48 \
	    "$$svgname" --export-png="raspi_door/res/image/$$fname.png" ; \
	done
