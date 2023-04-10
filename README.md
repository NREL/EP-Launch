# EP-Launch3

[![GitHub release](https://img.shields.io/github/release/nrel/ep-launch.svg?style=for-the-badge)](https://github.com/nrel/ep-launch/releases/latest)

Cross platform replacement for EP-Launch for EnergyPlus, written in Python using the `tkinter` graphics library.

## Documentation

[![Documentation](https://img.shields.io/readthedocs/ep-launch?label=Docs&logo=read%20the%20docs&style=for-the-badge)](https://ep-launch.readthedocs.io/en/latest/?badge=latest)

The project is documented (currently very sparsely) using Sphinx, and automatically generated in [html](https://ep-launch.readthedocs.io/en/) by ReadTheDocs.

## Testing

[![PEP8 Enforcement](https://img.shields.io/github/actions/workflow/status/NREL/EP-Launch/flake8.yml?label=Flake8&logo=github&style=for-the-badge)](https://github.com/NREL/EP-Launch/actions/workflows/flake8.yml)
[![Unit Tests](https://img.shields.io/github/actions/workflow/status/NREL/EP-Launch/unit_tests.yml?label=Unit%20Tests&logo=github&style=for-the-badge)](https://github.com/NREL/EP-Launch/actions/workflows/unit_tests.yml)
[![Coverage Status](https://img.shields.io/coveralls/github/NREL/EP-Launch?label=Coverage&logo=coveralls&style=for-the-badge)](https://coveralls.io/github/NREL/EP-Launch?branch=main)

The project is tested using standard Python unit testing practices.
Each commit is automatically tested with Github Actions on Windows, Mac, Ubuntu 20.04 and Ubuntu 22.04.
The code coverage across platforms is collected on Coveralls.

## Releases

[![Releases](https://img.shields.io/github/actions/workflow/status/NREL/EP-Launch/pypi.yml?label=Releases&logo=github&style=for-the-badge)](https://github.com/NREL/EP-Launch/actions/workflows/pypi.yml)

When a tag is created in the GitHub Repo, Github Actions builds a Python wheel and uploads it to PyPi: https://pypi.org/project/ep-launch/.
The packages can be downloaded using standard `pip install energyplus-launch` commands.
Once Pip installed, desktop shortcuts and launchers can be configured using the `energyplus-launch-configure` command from the same Python environment.

## Development

Basic development dependencies are installed with `pip install -r requirements.txt`.
This cross platform GUI application is built around the tkinter framework, so no additional dependencies are needed for the GUI.
The application can be run by executing the module as `python -m eplaunch` file.
To run the unit test suite, simply execute `nosetests`.
Unit test results will appear in the console, and coverage results will be in a `cover` directory.
