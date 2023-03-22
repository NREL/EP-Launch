Development
===========

Setting up a development environment only requires a few steps, and is similar on each platform.

- Install Python 3.6+ using standard installer processes (apt on Linux, brew on Mac, and Windows packages from `Pythons website <https://python.org>`_).
- Clone EP-Launch repository using Git: ``git clone https://github.com/NREL/EP-Launch``
- Change into the cloned directory: ``cd EP-Launch``
- Set up a virtual environment where the Python dependencies can be installed using ``python3 -m venv .\venv``
- Activate the virtual environment as needed (activate scripts will live in venv/bin/...)
- Install dependencies using ``pip install -r requirements.txt``
- At this point you should be able to run EP-Launch: ``python3 eplaunch\runner.py``
- You can also run the test suite by executing the nose test binary: ``nosetests``
