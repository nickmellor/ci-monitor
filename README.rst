CI Monitor
==========

Monitors the latest CI builds and reflects the results on a traffic light
and Geckoboard.


Installation on Linux
=====================

Install Python > 3.3

In project root,

pip install -r requirements.txt


Installation On Windows
=======================

This is useful for QAs and developers tasked with tracking the status of the build. The monitor can run
on your own laptop, perhaps as a startup app.

Install Python 3.5 or greater

After adding Python to PATH (environment variable),

pip install -r requirements.txt

There are libraries that may require a C compiler in order for them to install correctly. In Python, this is a
pain point when you're installing Python packages in Windows.

If there are errors, see this article:

https://blogs.msdn.microsoft.com/pythonengineering/2016/04/11/unable-to-find-vcvarsall-bat/

and be prepared to install Visual C++ Build Tools 2015 as detailed there.

then rerun:

pip install -r requirements.txt


Developers
==========


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

listener (class):
  - each listener instance checks one condition (defined in config) and returns results through exposed methods


Merge listener
--------------

The merge listener clones git repos in temporary directories and checks for unmerged branches (usually release and
hotfix branches.)

Due to some difficulties deleting temporary directories from Python apps under Windows at Medibank,
the app currently *does not* delete cloned repos, and you should not that it clones afresh each time the repo is polled.
This means temporary directories should be cleaned out regularly, and the merge check should not be run more often than
once a day.