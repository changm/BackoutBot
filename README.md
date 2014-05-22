BackoutBot
==========

Finds and backs out performance regressions for GAIA only.

## PreRequisites
* Python        // Main Script
* GitPython     // Used to access Gaia revisions
* b2gperf       // Used to test start up time
* python-hglib  // Used to access Gecko Revisions

For apps that have data in them like Music, Gallery, or Contacts, you need an SD card

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

Finally, if a regression is detected, it will output in regressions.txt

## Config
Modify config.txt to the location of your gecko / gaia directory

## Running
Easy thing to do is just do ./run.sh. This will move your gaia commit one commit forward.

If you need to run one commit again, you can run python main.py

If you want to run the next commit without running forever, ./runOnce.sh

## Updating Gecko
You have to manually update Gecko. The Gecko revision is read from the config.txt file, so you should flash from that gecko directory
