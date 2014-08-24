'''
Created on Sep 16, 2012

@author: jvtm

Plan:
 - generic parser function
 - different formatters: GPX, Pythonic values, ...
     (it would be silly to convert some text values to python and then back...)
 - optionally merging different sample blocks
 - pausing? get example data
 - waypoints / lap times?
'''

from cStringIO import StringIO
from datetime import timedelta
import sys
import dateutil.parser
import math

try:
    import lxml.etree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def parse_utc(text):
    """ with or without millisecs """
    return dateutil.parser.parse(text)


def parse_time(text):
    """ seconds since start """
    return timedelta(seconds=float(text))


def parse_hr(text):
    """ heart rate seems to be beats-per-second, convert to bpm """
    return int(60 * float(text))


def parse_rad(text):
    """ coordinates from rad -> deg """
    return math.degrees(float(text))


def parse_temperature(text):
    """ temperature from kelvin -> celsius """
    celsius = float(text) - 273.15
    return round(celsius, 1)

# Very temp. only single track segment.
GPX_TEMP_HDR = \
'''<?xml version="1.0" encoding="UTF-8" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     version="1.1"
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<trk>
<trkseg>
'''

GPX_TEMP_FTR = '''
</trkseg>
</trk>
</gpx>
'''


TRKPT_TEMPLATE = \
'''<trkpt lat="{Latitude}" lon="{Longitude}">
  <ele>{GPSAltitude}</ele>
  <time>{UTC}</time>
  <extensions>
    <gpxtpx:TrackPointExtension>
      <gpxtpx:hr>{HR}</gpxtpx:hr>
    </gpxtpx:TrackPointExtension>
  </extensions>
</trkpt>
'''

# XXX: if outputting strings anyway, there's no need to parse floats...
PARSERS = {
    # on both sample entry types
    'Time': parse_time,     # time from start. need to check how pausing affects this...
    #'UTC': parse_utc,       # it actually would work as GPX <time> directly
    'UTC': str,

    # GPS sample entry
    'Latitude': parse_rad,
    'Longitude': parse_rad,
    'GPSAltitude': float,     # TODO: compare against baro
    'GPSHeading': float,    # convert?
    'EHPE': float,   # TODO: find out what igotu2gpx outputs

    # Suunto sample entry
    'VerticalSpeed': float,             # m/s
    'HR': parse_hr,
    'EnergyConsumption': float,         # float, but what...
    'Temperature': parse_temperature,   # kelvins? really? :)
    'SeaLevelPressure': float,          # ???
    'Altitude': int,                    # XXX: from baro?
    'Distance': int,
    'Speed': float,                     # m/s
}


def fix_ambit_data(file_obj):
    data = file_obj.readline()
    data += "<root>"
    data += file_obj.read()
    data += "</root>\n"
    return StringIO(data)


def parse_ambit_samples(file_obj):
    # ambit data is not valid xml. need to add a fake top level entry.
    tree = ET.parse(file_obj)
    item = {}
    for sample in tree.find('samples'):
        is_gps_sample = (sample.find('Latitude') is not None)
        for child in sample:
            parser = PARSERS.get(child.tag)
            if not callable(parser):
                continue
            item[child.tag] = parser(child.text)
        if is_gps_sample:
            # merging data. gps samples have full seconds, so it's kinda nicer...
            yield item
            item = {}

if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as fob:
        samples = list(parse_ambit_samples(fix_ambit_data(fob)))

    sys.stdout.write(GPX_TEMP_HDR)
    # with my latest workouts (2013/03 and onwards) some samples are missing GPSAltitude
    # some modifications to this script/lib will follow "soon" to make this a little
    # bit prettier...
    althack = 0
    for sample in samples:
        if 'GPSAltitude' not in sample:
            sample['GPSAltitude'] = althack
        else:
            althack = sample['GPSAltitude']
        sys.stdout.write(TRKPT_TEMPLATE.format(**sample))
    sys.stdout.write(GPX_TEMP_FTR)

