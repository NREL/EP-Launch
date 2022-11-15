from pathlib import Path
from setuptools import setup

from eplaunch import NAME, VERSION


readme_file = Path(__file__).parent.resolve() / 'README.md'
readme_contents = readme_file.read_text()

setup(
    name=NAME,
    version=VERSION,
    description='Graphical Interface and Workflow Manager for EnergyPlus',
    url='https://github.com/NREL/EP-Launch',
    license='ModifiedBSD',
    packages=[
        'eplaunch', 'eplaunch.interface', 'eplaunch.utilities', 'eplaunch.workflows', 'eplaunch.workflows.default'
    ],
    package_data={"eplaunch.interface": ["resources/*.png", "resources/*.ico"]},
    include_package_data=True,
    long_description=readme_contents,
    long_description_content_type='text/markdown',
    author="Jason Glazer and Edwin Lee for the United States Department of Energy",
    install_requires=[],
    entry_points={
        'console_scripts': ['eplaunch=eplaunch.tk_runner:main_gui']
    }
)
