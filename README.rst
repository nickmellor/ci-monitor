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

External libraries used
-----------------------

- requests
- cleware traffic light control program (included in the repo)
- PyYAML

pip install-- for some libraries use:

python -m pip install <library>

from the command line. Works better!


IMPLEMENTATION NOTES
--------------------

heartbeat (config): shortest unit of time used by CI-Monitor

configuration: uses conf.yaml in project root
  - config directory contains examples
  - configuration needs love: cascading defaults needed like the schedule functionality

indicator (class):
  - loads "monitors" and schedules them based on config
  - polls for results from monitors
  - communicates results on (logging, sounds, traffic light etc.)
  - modularising this part of the app is in progress

monitor (class):
  - each monitor checks one condition and returns results through exposed methods

ostruct (library): used mainly to simplify reading config
  - config.defaults.sounds.failure rather than config['defaults']['sounds']['failure']

schedule (library): excellent little library used to schedule monitoring tasks