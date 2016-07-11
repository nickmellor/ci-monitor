CI Monitor
==========

Monitors the latest CI builds and reflects the results on a traffic light
and Geckoboard.


On Raspberry Pi
===============

- Runs on a Raspberry Pi Linux box as a Python 3 script
- ci_monitor.py auto-run from /etc/rc.local at bootup

On Windows
==========

This is useful for testers and developers tasked with tracking the status of the build. The monitor can run
on any number of machines independently

Suggest setting up as a py2exe project:

python setup.py py2exe

then set up a shortcut to run ci_monitor.exe in the dist directory (working directory set to project root so it can find
active config file.)

Setup
=====

Note on pip install:

For some libraries (especially XML libraries on Windows):

python -m pip install -r requirements.txt

from the command line works better than

pip install -r requirements.txt


External libraries used
-----------------------

CI Monitor is a python 3 app.

see requirements.txt

ostruct (library): used mainly to simplify reading config
  - config.defaults.sounds.failure rather than config['defaults']['sounds']['failure']

schedule (library): used to schedule monitoring tasks


IMPLEMENTATION NOTES
--------------------

heartbeat (config): shortest unit of time used by CI-Monitor. If nothing's happening, CI monitor waits
    for a heartbeat

configuration:
  - looks for CIMCONFIG environment variable (filename without .yaml). If not present, 'default'
  - configs directory contains examples
  - configuration needs love: more cascading defaults needed (cf schedules)

indicator (class):
  - loads "monitors" and schedules them based on YAML config file
  - polls for results from monitors
  - communicates results on (logging, sounds, traffic light etc.)
  - modularising this part of the app is in progress
  - logging needs attention-- dropped out of submodules

monitor (class):
  - each monitor instance checks one condition (defined in config) and returns results through exposed methods