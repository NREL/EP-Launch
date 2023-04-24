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
        'eplaunch', 'eplaunch.interface', 'eplaunch.utilities', 'eplaunch.workflows', 'eplaunch.workflows.default',
    ],
    package_data={
        "eplaunch": ["icons/*.png", "icons/*.ico", "icons/*.icns"],
        "eplaunch.interface": ["resources/*.png"]
    },
    include_package_data=True,
    long_description=readme_contents,
    long_description_content_type='text/markdown',
    author="Jason Glazer and Edwin Lee for the United States Department of Energy",
    install_requires=['PLAN-Tools>=0.7', 'tkmacosx'],
    entry_points={
        'gui_scripts': [
            'energyplus_launch=eplaunch.tk_runner:main_gui',
        ],
        'console_scripts': [
            'energyplus_launch_configure=eplaunch.configure:configure_cli',
            'energyplus_launch_workflow_tester=eplaunch.workflows.workflow_tester:cli'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Utilities',
    ],
    platforms=[
        'Linux (Tested on Ubuntu)', 'MacOSX', 'Windows'
    ],
    keywords=[
        'energyplus_launch', 'ep_launch',
        'EnergyPlus', 'eplus', 'Energy+',
        'Building Simulation', 'Whole Building Energy Simulation',
        'Heat Transfer', 'HVAC', 'Modeling',
    ]
)
