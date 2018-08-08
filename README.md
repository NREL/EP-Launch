# EP-Launch3

[![GitHub release](https://img.shields.io/github/release/nre/ep-launch.svg)](https://github.com/nrel/ep-launch/releases/latest)

Cross platform replacement for EP-Launch for EnergyPlus

## Documentation

[![Documentation Status](https://readthedocs.org/projects/ep-launch/badge/?version=latest)](https://ep-launch.readthedocs.io/en/latest/?badge=latest)

The project is documented (currently very sparsely) using Sphinx, and automatically generated in [html](https://ep-launch.readthedocs.io/en/) by ReadTheDocs.

## Testing

[![](https://travis-ci.org/NREL/EP-Launch.svg?branch=master)](https://travis-ci.org/NREL/EP-Launch)
[![Build status](https://ci.appveyor.com/api/projects/status/ortmjm0tu2o43x93/branch/master?svg=true)](https://ci.appveyor.com/project/Myoldmopar/ep-launch/branch/master)
[![Coverage Status](https://coveralls.io/repos/github/NREL/EP-Launch/badge.svg?branch=master)](https://coveralls.io/github/NREL/EP-Launch?branch=master)

The project is tested using standard Python unit testing practices.
Each commit is automatically tested on Linux and Mac on [Travis-CI](https://travis-ci.org/NREL/EP-Launch).
The Linux tests provide the code coverage metric.
Each commit is also tested on Windows on [AppVeyor](https://ci.appveyor.com/project/Myoldmopar/ep-launch).
When a tag is created in the GitHub Repo, both Travis and AppVeyor also build deployment packages and post them to the release.

## Development

This cross platform GUI application is built around the wxPython (Phoenix) framework.
For details about all the nuances of installing this library, read through the requirements.txt file.
Once you have wx installed, you can pip install the rest of the requirements that are called out in the requirements file.
The application can be run by executing the eplaunch/runner.py file.
To execute all the unit tests, just execute `setup.py test`.