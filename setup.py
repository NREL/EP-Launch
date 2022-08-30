import codecs
import os
from setuptools import setup, find_packages

from eplaunch import NAME, VERSION

this_dir = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(this_dir, 'README.md'), encoding='utf-8') as i_file:
    long_description = i_file.read()

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(exclude=['test', 'tests', 'test.*']),
    description='Graphical Interface and Workflow Manager for EnergyPlus',
    url='https://github.com/NREL/EP-Launch',
    license='ModifiedBSD',
    author='DOE',
    author_email='d@d.d',
    long_description=long_description,
    long_description_content_type='text/markdown',
    test_suite='nose.collector',
    tests_require=['nose'],
    keywords='energyplus',
    include_package_data=True,
    install_requires=['wxpython', 'pypubsub',
                      # Temporary until wxpython fixes it
                      'attrdict3'],
    entry_points={
        'console_scripts': ['eplaunch3=eplaunch.runner:main'],
    },
    python_requires='>=3.5',
)
