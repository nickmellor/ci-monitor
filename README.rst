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

*** NO LONGER WORKING-- not compatible with dynamic importing of libraries

Set up a shortcut to run ci_monitor.exe in the dist directory (working directory set to *project root* so it can find
configs etc.)

Developer
---------

Note on pip install:

For some libraries (e.g. XML libraries on Windows):

python -m pip install -r requirements.txt

if installing under Windows and you get errors like "can't find VCVARSALL.BAT" you probably need to install Visual Studio or Visual C++ build tools

http://download.microsoft.com/download/5/f/7/5f7acaeb-8363-451f-9425-68a90f98b238/visualcppbuildtools_full.exe

before pip can install some of the requirements.

For an explanation, see:

https://blogs.msdn.microsoft.com/pythonengineering/2016/04/11/unable-to-find-vcvarsall-bat/

If upgrading from within PyCharm doesn't work, try this on the command line, from the project root:

python -m pip install -r requirements.txt


External libraries used
-----------------------

CI Monitor is a python 3 app.

ostruct (library): used mainly to simplify reading config
  - config.defaults.sounds.failure rather than config['defaults']['sounds']['failure']

schedule (library): used to schedule monitoring tasks

see also requirements.txt


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