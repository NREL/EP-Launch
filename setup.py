from setuptools import setup

setup(
    name='EPLaunch3',
    version='0.1',
    packages=['eplaunch', 'eplaunch.interface'],
    url='https://energyplus.net',
    license='ModifiedBSD',
    author='DOE',
    author_email='webmaster@doe.gov',
    description='Graphical Interface and Workflow Manager for EnergyPlus',
    scripts='eplaunch/runner.py',
    test_suite="eplaunch.tests",
)
