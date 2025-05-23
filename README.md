# Realtime AIS filter

This tool is intended to use in conjunction with the [Bridge command](https://www.bridgecommand.co.uk/) ship simulation/training environment and a chart plotter such as [OpenCPN](https://opencpn.org/) to simulate vessels turning off their AIS.

aisfilter.py listens for NMEA data on UDP on localhost on the default port used by Bridge command and relays this over TCP as a server on localhost:101111 to which you should configure OpenCPN to connect.

Once set up this way, aisfilter.py provides a simple interactive command language:

* "l<ENTER>" lists all seen and/or filtered MMSI:s
* "MMSI<ENTER>" will toggle filtering that MMSI
* "t<ENTER>" will toggle all AIS on/off

Note that non-ais NMEA messages (such as GPS) are always just passed through no matter what.
