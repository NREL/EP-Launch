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

Future Work
-----------

Timestamps need to be added to the run data to easily check for stale results when input files are changed.


Cache Module Auto-Documentation
-------------------------------

This is the auto-generated documentation of the Cache module that may provide a deeper understanding of the topics described above.

.. automodule:: eplaunch.utilities.cache
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:
