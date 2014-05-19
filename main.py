import os
import git
import subprocess
import os
import hglib

GECKO_DIR=""
GAIA_DIR=""
B2G_PERF_DIR=""

# Need to get a sd card to test
#GAIA_APPS_TO_TEST=["Settings", "Camera", "Phone"]
GAIA_APPS_TO_TEST=["Settings"]

def ReadConfig():
  file = open('config.txt', 'r')
  config = {}

  for line in file.readlines():
    options = line.split("=")
    option = options[0].strip()
    value = options[1].strip()
    config[option] = value

  file.close()
  return config

def ParseConfigs(config):
  global GAIA_DIR
  global GECKO_DIR

  GAIA_DIR = config['GAIA_DIR']
  GECKO_DIR = config['GECKO_DIR']

def GetGaiaRevision(gaiaDirectory):
  print "\nGetting Gaia Revision from directory" + gaiaDirectory
  repo = git.Repo(gaiaDirectory)
  master = repo.heads.master
  commit = master.commit

  print "Basing off Gaia master commit: " + str(commit)
  return commit

def GetGeckoRevision(geckoDir):
  print "\nGetting Gecko Revision from: " + str(geckoDir)
  client = hglib.open(geckoDir)
  tip = client.tip()
  commit = str(client.tip().rev) + ":" + str(client.tip().node)

  print "Basing off Gecko master commit: " + str(commit)
  return commit

def FlashGaia(gaiaDir):
  print "\nFlash Gaia from directory: " + str(gaiaDir)
  os.chdir(gaiaDir)
  env = os.environ

  # ignore first time user
  env["NOFTU"] = "1"

  subprocess.call(["make", "reset-gaia"])

  print "Flashed Gaia, rebooting device.... Sleeping for 2 minutes"
  subprocess.call(["adb", "reboot"])
  time.sleep(120)

def RunStartupTest(appName, results):
  args = "--delay=10 --iterations=30 " + str(appName)
  print "Running b2g perf for app: " + str(appName)
  output = subprocess.call(["b2gperf", "--delay=10", "--iterations=20", str(appName)])
  length = len(output)
  lastLine = output[length - 1].strip()
  print lastLine

def RunB2GPerf(b2gPerfDir):
  print "\nRunning B2g Perf"
  subprocess.call(["adb", "forward", "tcp:2828", "tcp:2828"])
  results = {}

  for test in GAIA_APPS_TO_TEST:
    RunStartupTest(test, results)

  #subprocess.call(["b2gperf", "--delay=10 --iterations=30 Contacts"])
  #results['startup'] = 30
  return results

def ReportResults(results):
  print "Printing Results "
  print(results)

def Main():
  global GECKO_DIR
  global GAIA_DIR
  global B2G_PERF_DIR

  config = ReadConfig()
  ParseConfigs(config)
  gaiaRev = GetGaiaRevision(GAIA_DIR)
  geckoRev = GetGeckoRevision(GECKO_DIR)

  #FlashGaia(GAIA_DIR)
  startupTimes = RunB2GPerf(B2G_PERF_DIR)
  #ReportResults(startupTimes)

Main()
