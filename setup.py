#     packages=['eplaunch', 'eplaunch.interface'],
#     scripts='eplaunch/runner.py',
#     test_suite="eplaunch.tests",


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

setup(
    name="EP-Launch",
    version="0.1",
    author='Jason Glazer and Edwin Lee for the United States Department of Energy',
    description='Graphical Interface and Workflow Manager for EnergyPlus',
    url='https://github.com/NREL/EP-Launch',
    license='ModifiedBSD',
    options={"build_exe": build_exe_options},
    executables=[Executable("eplaunch/runner.py", targetName="EPLaunch", base=base)]
)
