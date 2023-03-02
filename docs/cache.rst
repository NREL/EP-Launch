Cache File Operation
====================

This documents how caching works within EP-Launch.
Caching is how workflow runs and output data are persisted on disk.

High Level Overview
-------------------

At a high level, caching simply occurs by persisting a JSON file in a run directory.
When a workflow starts, if the cache file does not exist, it is created.
If it already exists, it is read, updated, and re-written.
The cache file includes input parameters, including workflow name, and output parameters as defined by the workflow.
When a workflow is done, the cache file for that directory is updated with output data.
When a user browses to a folder in EP-Launch, if it has a cache file, that is parsed and previous output data is shown.

Detailed Operation
------------------

In real operation within EP-Launch, there are complications that make the operation a difficult problem:

- EP-Launch allows multiple workflows to be running, even within the same folder, and on the same file.
- It is completely uncertain as to when workflows will complete, two workflows could complete in the same directory at essentially the same time.

The full documentation of the CacheFile class is shown below: :ref:`Cache Module Auto-Documentation`.
The GUI creates instances of this class to read or write cache data to disk.
This list covers the important parts of the caching operation in EP-Launch:

- When a new folder is selected, a CacheFile instance is created to read data from disk, then released.
- When a workflow is run, a CacheFile in the current directory is opened and workflow parameters are written, including workflow name, weather file name, and other data.
- When a workflow is completed, a CacheFile is retrieved for the workflow's directory, results are added from the workflow, and the cache is written.

Cache File Layout
-----------------

The cache file is a simple JSON file.
At the root of the JSON is an object with a single key "workflows", that captures the entire context
The value of this key is another object with keys for each workflow.
The value of each workflow key is an object with a single key, "files", whose keys correspond to files that have been run for this workflow.
Each file object has two keys: "config" and "result".
The config key captures any input data related to this run, for now it is only weather data.
The result key captures all the output column data corresponding to this workflow run.

An example of the layout is provided here::

    {
      "workflows": {
        "Get Site:Location": {
          "files": {
            "1ZoneEvapCooler.idf": {
              "config": {
                "weather": ""
              },
              "result": {
                "Site:Location []": "Denver Centennial CO USA WMO=724666"
              }
            }
          }
        },
        "EnergyPlus 8.9 SI": {
          "files": {
            "1ZoneEvapCooler.idf": {
              "config": {
                "weather": "MyWeather.epw"
              },
              "result": {
                "Errors": 0,
                "Warnings": 1,
                "Runtime [s]": 1.23,
                "Version": "8.9"
              }
            },
            "RefBldgMediumOfficeNew2004_Chicago.idf": {
              "config": {
                "weather": ""
              },
              "result": {
                "Errors": 0,
                "Warnings": 4,
                "Runtime [s]": 1.58,
                "Version": "8.9"
              }
            }
          }
        }
      }
    }

Future Work
-----------

Timestamps need to be added to the run data to easily check for stale results when input files are changed.


Cache Module Auto-Documentation
-------------------------------

This is the auto-generated documentation of the Cache module that may provide a deeper understanding of the topics described above.

.. automodule:: energyplus_launch.utilities.cache
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:
