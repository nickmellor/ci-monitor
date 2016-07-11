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

Casual user
-----------

Easiest way is to run as a a py2exe project. From project directory:

Set up a shortcut to run ci_monitor.exe in the dist directory (working directory set to *project root* so it can find
configs etc.)

Developer
---------

python setup.py py2exe updates the ci_monitor.exe. This is best pushed with code changes so ci-monitor works out of the
box without needing to know the mechanics of installing Python libraries (which can be non-trival under Windows)

Note on pip install:

For some libraries (especially XML libraries on Windows):

python -m pip install -r requirements.txt

from the command line works better than

pip install -r requirements.txt


External libraries used
-----------------------

CI Monitor is a python 3 app.

ostruct (library): used mainly to simplify reading config
  - config.defaults.sounds.failure rather than config['defaults']['sounds']['failure']

schedule (library): used to schedule monitoring tasks

see requirements.txt


IMPLEMENTATION NOTES
--------------------

heartbeat (config): shortest unit of time used by CI-Monitor. If nothing's happening, CI monitor waits
    for a heartbeat

configuration:
  - looks for CIMCONFIG environment variable (filename without .yaml). If not present, assumes 'default'
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