# EP-Launch3

[![Documentation Status](https://readthedocs.org/projects/ep-launch/badge/?version=latest)](https://ep-launch.readthedocs.io/en/latest/?badge=latest)

Cross platform replacement for EP-Launch for EnergyPlus

## Testing

[![](https://travis-ci.org/NREL/EP-Launch.svg?branch=master)](https://travis-ci.org/NREL/EP-Launch)
[![Coverage Status](https://coveralls.io/repos/github/NREL/EP-Launch/badge.svg?branch=master)](https://coveralls.io/github/NREL/EP-Launch?branch=master)

The source is tested using the python unittest framework.  To execute all the unit tests, just execute `setup.py test`.  The tests are also executed by [Travis CI](https://travis-ci.org/NREL/EP-Launch).

## Development

This cross platform GUI application is built around the wxPython (Phoenix) framework.
For details about all the nuances of installing this library, read through the requirements.txt file.
Once you have wx installed, you can pip install the rest of the requirements that are called out in the requirements file.
The application can be run by executing the eplaunch/runner.py file.
