# EP-Launch3

[![GitHub release](https://img.shields.io/github/release/nrel/ep-launch.svg?style=for-the-badge)](https://github.com/nrel/ep-launch/releases/latest)

Cross platform replacement for EP-Launch for EnergyPlus

## Documentation

[![Documentation](https://img.shields.io/readthedocs/ep-launch?label=Docs&logo=read%20the%20docs&style=for-the-badge)](https://ep-launch.readthedocs.io/en/latest/?badge=latest)

The project is documented (currently very sparsely) using Sphinx, and automatically generated in [html](https://ep-launch.readthedocs.io/en/) by ReadTheDocs.

## Testing

[![Unit Tests](https://img.shields.io/github/workflow/status/NREL/EP-Launch/Unit%20Tests?label=Unit%20Tests&logo=github&style=for-the-badge)](https://github.com/NREL/EP-Launch/actions?query=workflow%3A%22Unit+Tests%22)
[![Coverage Status](https://img.shields.io/coveralls/github/NREL/EP-Launch?label=Coverage&logo=coveralls&style=for-the-badge)](https://coveralls.io/github/NREL/EP-Launch?branch=master)
[![PEP8 Enforcement](https://img.shields.io/github/workflow/status/NREL/EP-Launch/Flake8?label=Flake8&logo=github&style=for-the-badge)](https://github.com/NREL/EP-Launch/actions?query=workflow%3AFlake8)
[![Releases](https://img.shields.io/github/workflow/status/NREL/EP-Launch/Releases?label=Releases&logo=github&style=for-the-badge)](https://github.com/NREL/EP-Launch/actions?query=workflow%3AReleases)

The project is tested using standard Python unit testing practices.
Each commit is automatically tested with Github Actions on Windows, Mac, Ubuntu 18.04 and Ubuntu 20.04.
The code coverage across platforms is collected on Coveralls.
When a tag is created in the GitHub Repo, Github Actions builds downloadable packages.

## Development

This cross platform GUI application is built around the wxPython (Phoenix) framework.
For details about all the nuances of installing this library, read through the requirements.txt file.
Once you have wx installed, the only other dependency needed to run the program is `PyPubSub` via `pip install pypubsub`.
The application can be run by executing the eplaunch/runner.py file.

To run the unit test suite, make sure to have nose and coverage installed via: `pip install nose coverage`.
Then execute `setup.py nosetests`.
Unit test results will appear in the console, and coverage results will be in a `cover` directory.
