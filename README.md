BackoutBot
==========

Finds and backs out performance regressions.

## PreRequisites
Python        // Main Script
GitPython     // Used to access Gaia revisions
b2gperf       // Used to test start up time
python-hglib  // Used to access Gecko Revisions

## Installing Requirements:

Hopefully the easy way - run setup.sh

GitPython - https://gitorious.org/git-python
Run: easy\_install gitpython

b2g perf - https://github.com/mozilla/b2gperf
Run: pip install b2gperf

pip install python-hglib
run: pip install python-hglib

## Expected Output:
For each app, you will get APPNAME.results.txt
It will contain the b2gperf output

In addition, a results.log.txt will contain the Gecko / Gaia revision
and the median, mean, and std deviation of the cold launch time.

The log is appended to after each run, right now we have to manually clean it.
