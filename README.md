BackoutBot
==========

Finds performance regressions for GAIA only. Doesn't back you out.... YET.

## PreRequisites
* Python        // Main Script
* GitPython     // Used to access Gaia revisions
* b2gperf       // Used to test start up time
* python-hglib  // Used to access Gecko Revisions

For apps that have data in them like Music, Gallery, or Contacts, you need an SD card

## Installing Requirements:

Hopefully the easy way - run setup.sh. This should install all the reqs for you.

GitPython - https://gitorious.org/git-python

Run: easy\_install gitpython

b2g perf - https://github.com/mozilla/b2gperf

Run: pip install b2gperf

python-hglib

Run: pip install python-hglib

## Expected Output:
For each app, you will get APPNAME.results.txt
It will contain the b2gperf output.

In addition, a results.log.txt will contain the Gecko / Gaia revision.
and the median, mean, and std deviation of the cold launch time.

The log is appended to after each run, right now we have to manually clean it.

Finally, if a regression is detected, it will output in regressions.txt

## Config
Modify config.txt to point to the location of your gecko / gaia directory

## Running
Easy thing to do is just do ./run.sh. This will move your gaia directory one commit forward.

If you need to run one commit again, you can run python main.py

If you want to run the next commit without running forever, ./runOnce.sh

## Updating Gecko
You have to manually update Gecko. The Gecko revision is gecko directory read from the config.txt file, so you should flash from that gecko directory. Try to update Gecko once every day or two.

## FAQ
  1. I can't install any of the requirements? It says Permission denied!

  We try to install the python libraries using pip, which has to write some files to your python install directory. This is probably somewhere in /Library, which needs sudo access. Try using sudo. I know, I'm evil and bad, but oh so lazy.

  2. b2gperf isn't working anymore!

  Sometimes b2gperf is updated along with Gecko. Please update Gecko and run the setup.sh script again. This will update b2gperf and Gecko so that they are in sync again.

  3. Sometimes b2gperf times out and I lost some data!

  Yeah... not sure if this is marionnette or b2gperf or what. If you just continue running, it'll eventually fix itself.

![ScreenShot](/images/backout.jpg)
