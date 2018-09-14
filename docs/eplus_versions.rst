EnergyPlus Version Mechanics
============================

This document will cover a few aspects of EP-Launch and how it handles EnergyPlus versions.  This will include:

- How the GUI auto finds E+ versions
- How the version is tracked alongside workflow instances
- How the version is parsed
- How different versions are displayed
- Issues with two workflows having the same name (without a version specified)

In addition, maybe this will also include thoughts for future work:

- Instead of trying to parse out the version, what if the workflow was modified to include a new abstract function (get_ep_version).
  This function could return False if the workflow doesn't belong to an E+ version, or the version ID if it does
- Then what if we just captured the scope of the workflow as the containing folder, and only used the E+ version for specifically version translation or something.