# from setuptools import setup
#
# setup(
#     name='EPLaunch3',
#     version='0.1',
#     packages=['eplaunch', 'eplaunch.interface'],
#     url='https://energyplus.net',
#     license='ModifiedBSD',
#     author='DOE',
#     author_email='webmaster@doe.gov',
#     description='Graphical Interface and Workflow Manager for EnergyPlus',
#     scripts='eplaunch/runner.py',
#     test_suite="eplaunch.tests",
#     options={"py2exe": {"compressed": 2,
#                         "optimize": 2,
#                         "includes": [],
#                         "excludes": [],
#                         "packages": [],
#                         "dll_excludes": [],
#                         "bundle_files": 3,
#                         "dist_dir": "dist",
#                         "xref": False,
#                         "skip_archive": False,
#                         "ascii": False,
#                         "custom_boot_script": '',
#                         }
#              },
#     windows=['sampleApp.py']
# )

import glob
import os
import sys

from cx_Freeze import setup, Executable

include_files = []
default_workflows = glob.glob("eplaunch/workflows/default/*.py")
workflow_tuples = [(x, os.path.join('lib', x)) for x in default_workflows]
include_files.extend(workflow_tuples)

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
      "packages": ["eplaunch", "os"],
      "excludes": ["tkinter"],
      "include_files": include_files
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="EP-Launch",
      version="0.1",
      description="My GUI application!",
      options={"build_exe": build_exe_options},
      executables=[Executable("eplaunch/runner.py", targetName="EPLaunch", base=base)])
