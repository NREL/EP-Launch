# EP-Launch3

[![GitHub release](https://img.shields.io/github/release/nrel/ep-launch.svg?style=for-the-badge)](https://github.com/nrel/ep-launch/releases/latest)

Cross platform replacement for EP-Launch for EnergyPlus, written in Python using the `tkinter` graphics library.

## Documentation

[![Documentation](https://img.shields.io/readthedocs/ep-launch?label=Docs&logo=read%20the%20docs&style=for-the-badge)](https://ep-launch.readthedocs.io/en/latest/?badge=latest)

The project is documented (currently very sparsely) using Sphinx, and automatically generated in [html](https://ep-launch.readthedocs.io/en/) by ReadTheDocs.

## Testing

[![PEP8 Enforcement](https://img.shields.io/github/workflow/status/NREL/EP-Launch/Flake8?label=Flake8&logo=github&style=for-the-badge)](https://github.com/NREL/EP-Launch/actions?query=workflow%3AFlake8)
[![Unit Tests](https://img.shields.io/github/workflow/status/NREL/EP-Launch/Run%20Tests?label=Unit%20Tests&logo=github&style=for-the-badge)](https://github.com/NREL/EP-Launch/actions/workflows/unit_tests.yml)
[![Coverage Status](https://img.shields.io/coveralls/github/NREL/EP-Launch?label=Coverage&logo=coveralls&style=for-the-badge)](https://coveralls.io/github/NREL/EP-Launch?branch=master)

The project is tested using standard Python unit testing practices.
Each commit is automatically tested with Github Actions on Windows, Mac, Ubuntu 18.04 and Ubuntu 20.04.
The code coverage across platforms is collected on Coveralls.

## Releases

[![Releases](https://img.shields.io/github/workflow/status/NREL/EP-Launch/Release_to_PyPi?label=Releases&logo=github&style=for-the-badge)](https://github.com/NREL/EP-Launch/actions/workflows/pypi.yml)

When a tag is created in the GitHub Repo, Github Actions builds a Python wheel and uploads it to PyPi: https://pypi.org/project/ep-launch/.
The packages can be downloaded using standard `pip install ep-launch` commands.

## Development

Basic development dependencies are installed with `pip install -r requirements.txt`.
This cross platform GUI application is built around the tkinter framework, so no additional dependencies are needed for the GUI.
The application can be run by executing the `eplaunch/tk_runner.py` file.

To run the unit test suite, simply execute `nosetests`.
Unit test results will appear in the console, and coverage results will be in a `cover` directory.
