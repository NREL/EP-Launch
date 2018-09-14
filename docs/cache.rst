Cache File Operation
====================

This documents how caching works within EP-Launch.
Caching represents how workflow runs and output data are persisted on disk.

High Level Overview
-------------------

At a high level, caching simply occurs by persisting a JSON file in a run directory.
When a workflow starts, if the cache file does not exist, it is created.
If it already exists, it is read, updated, and re-written.
The cache file includes input parameters, including workflow name, and output parameters as defined by the workflow.

Detailed Operation
------------------

The previous section describes cache file operation in a very straightforward manner, however, in real operation within EP-Launch, there are a number of reasons why it is not so simple:

- EP-Launch allows multiple workflows to be running, even within the same folder, and on the same file.
- It is completely uncertain as to when workflows will complete, two workflows could complete in the same directory at essentially the same time.

Handling issues like this led to the following design features for caching:

- Locking mechanism
- Storage
- Other

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
