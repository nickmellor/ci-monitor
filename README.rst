CI Monitor
==========

Open-source monitor for Continuous Integration build pipeline. Can also be used for monitoring production environments.

YAML-configured, and can easily be extended, as it has an open architecture. New 'listeners' can be added which are expert
at monitoring particular aspects of a system or pipeline. YAML configuration is polled regularly and will incorporate
any new listeners without needing a restart.

Monitor is designed to run continuously, hence the belt-and-braces exception-handling.

Currently there are listeners for:
  - CI builds (via Bamboo REST interface)
  - check git merges to master branches are complete
  - sitemap URLs availability

'Indicators' reflect the results returned by groups of these 'listeners', on a
[Cleware traffic light](http://www.cleware-shop.de/USB-MiniTrafficLight-EN), by emitting sounds
and by logging. Historically, has shown results on a [Geckoboard](http://www.geckoboard.com) via push notifications,
 and listened to a BSM monitoring service via REST.


Installation on Linux
=====================

Install Python > 3.3

In project root,

pip install -r requirements.txt


Installation On Windows
=======================

This is useful for tracking the status of builds. The monitor can run
on your own laptop, for example as a startup app. Useful for devs, devops, QAs and managers.

Install Python 3.3 or greater or create a virtualenv (http://docs.python-guide.org/en/latest/dev/virtualenvs/)

In project root:

pip install -r requirements.txt

There are libraries that may require a C compiler in order for them to install correctly. In Python, this is still
sometimes a pain point when you're installing Python packages in Windows.

If there are errors, see this article:

https://blogs.msdn.microsoft.com/pythonengineering/2016/04/11/unable-to-find-vcvarsall-bat/

and be prepared to install Visual C++ Build Tools 2015 as detailed there.

then rerun:

pip install -r requirements.txt


Configuration
=============

  - take a look at the examples
  - this app 'hot-configures'-- if you change the config, it will detect changes to settings and restart
  - CIMCONFIG environment var points to config file, e.g.
      export CIMCONFIG=merge # Bash
      set CIMCONFIG=merge # Windows
    If not present, assumes 'default'
  - global configs (in global.yaml) are loaded first, then overridden by config file above
  - configs directory contains examples
  - when config changes or CI-Monitor first starts, CI-Monitor comes over all optimistic and the lights go green.
    This is expected behaviour, and continues until the first configured listener returns a fail.
    (Is this behaviour the right one?)



Developers
==========


External libraries used
-----------------------

CI Monitor is a python >= 3.3 app.

ostruct (library): used mainly to simplify reading config
  - config.defaults.sounds.failure rather than config['defaults']['sounds']['failure']
  - has been used less lately, and is no longer consistently used (Jan 2017)

schedule (library): used to schedule monitoring tasks

see also requirements.txt


IMPLEMENTATION NOTES
--------------------

heartbeat (config): shortest unit of time used by CI-Monitor. CI monitor waits
    for at least a heartbeat before the next poll

configuration:
  - configuration needs love:
    * more cascading defaults needed (cf schedules)
    * more robust and informative when parts of config are missing
    * listeners and indicators should use a method to retrieve a setting, not dict syntax (would enable
      better error-handling)

indicator (class):
  - loads "listeners" and schedules them based on YAML config file
  - polls results from listeners
  - communicates results on (logging, sounds, traffic light etc.)
  - modularising this part of the app is in progress
  - logging needs attention-- dropped out of submodules

listener (class):
  - each listener instance checks one condition (defined in config) and returns results through exposed methods


Listener Notes
==============

Merge Listener
--------------

The merge listener clones git repos in temporary directories and checks for unmerged branches (usually release and
hotfix branches.)

Due to some difficulties deleting temporary directories from Python apps under Windows at Medibank,
the app currently *does not* delete cloned repos.

You should note that it clones afresh each time the repo is polled.

This means temporary directories should be cleaned out regularly, and the merge check should not be run too often.