pyambit
=======

Python library for Suunto Ambit data files


Suunto Ambit XML files
======================

Can be found on:

* Windows: `%HOMEPATH%\AppData\Roaming\Suunto\MovesLink2\`
* Mac OS X: `/Users/YOUR_USERNAME/Library/Application Support/Suunto/Moveslink2/`

Technically, these files are not XML, as they have multiple root elements.
As a workaround this library internally first injects a dummy root element
to the XML document (in memory).

_Update:_ as of Moveslink2 v1.2.8 the application now stores files like `26FBXXXXXXXXXXXX-2014-08-24T15_01_49-0.sml`.
These are actually valid XML, and now somewhat supported by this library (not fully confirmed yet).


Plans / TODO
============

* output to GPX (kinda done, not validated yet)
* test with different settings, recording intervals, sports etc
* check that output works nicely with QuickRoute (incl. HR etc)
* figure out rest of the remaining fields
* validate output
* track segment / split time support
* include something from the `header` section
* figure out what the occasional `IBI` section contains
* nice enough interface / class for non-GPX use cases
* test files in this repo (my regular files are maybe too big, 2-4MB)
* Python packaging (setup.py)
* Debian packaging (debian/)
* Windows usage instructions?


Test data
=========

Initially this library is only tested with running, orienteering & cycling
settings. At the moment only basic input files without gaps, splits etc
have been tested.


Links
=====

There is also a GPLv3 licensed project called ambit2gpx, it might or
might not do similar things.


