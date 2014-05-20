import os
import git
import subprocess
import os
import hglib
import re
import sys

GECKO_DIR=""
GAIA_DIR=""
B2G_PERF_DIR=""
RESULTS_FILE="results.txt"

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

# Returns a tuple with (median, mean, stdDev)
def ExtractStartupData(resultString):
  # Our string looks like: Results for Settings, cold_load_time: median:1945, mean:2008, std: 97, max:2146, min:1934, all:2146,1934,1945
  # strip out the median, mean, and std deviatoin numbers. Ugly Regex sadface
  regexResults = re.search("median:([0-9]+).*mean:([0-9]+).*std: ([0-9]+).*", resultString)
  if (regexResults == None):
    print "Could not find any start up data. Exiting"
    sys.exit(1)

  return regexResults.groups()

def WriteTestResults(appName, resultString, gaiaRevision, geckoRevision):
  global RESULTS_FILE
  file = open(RESULTS_FILE, 'w')
  lines = []
  lines.append("Results for: " + str(appName) + "\n")
  lines.append("Gaia Revision: " + str(gaiaRevision) + "\n\n")
  lines.append("Gecko Revision: " + str(geckoRevision) + "\n\n")

  lines.append(resultString)
  file.writelines(lines)
  file.close()

def GetLastResults(appName):
  global RESULTS_FILE
  file = open(RESULTS_FILE, "r")
  if (file is None):
    print "Could not open results file: " + str(RESULTS_FILE) + ". Setting new baseline"
    return (10000, 10000, 10000)

  lines = file.readlines()
  lines = "".join(lines)
  file.close()

  return ExtractStartupData(lines)

def DealWithRegression(previousResults, currentResults):
  previousMean = previousResults[1]
  currentMean = currentResults[1]
  print "AND WE HAVE A REGRESSION. Previous Mean: " + str(previousMean) + " current mean: " + currentMean

def PassTest(previousResults, currentResults):
  prevMean = previousResults[1]
  prevStd = previousResults[2]

  currentMean = currentResults[1]
  currentStdDev = currentResults[2]

  print "\nPassed Tests"
  print "Current mean: " + str(currentMean) + " std dev: " + str(currentStdDev)
  print "Previous mean: " + str(prevMean) + " std dev: " + str(prevStd)

# Each should be a tuple of (median, mean, stdDev)
def AnalyzeResults(previousResults, currentResults):
  previousMean = previousResults[1]
  previousStdDev = previousResults[2]

  threshold = previousMean + previousStdDev
  currentMean = currentResults[1]
  if (currentMean >= threshold):
    DealWithRegression(previousResults, currentResults)
  else:
    PassTest(previousResults, currentResults)

def RunStartupTest(appName, results, gaiaRev, geckoRev):
  args = "--delay=10 --iterations=30 " + str(appName)
  print "Running b2g perf for app: " + str(appName)
  command = "b2gperf --delay=10 --iterations=3 " + str(appName)
  proc = subprocess.Popen(["b2gperf", "--delay=10", "--iterations=3", str(appName)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()

  print err

  lastResults = GetLastResults(appName)
  WriteTestResults(appName, err, gaiaRev, geckoRev)
  currentResults = ExtractStartupData(err)

  AnalyzeResults(lastResults, currentResults)

def RunB2GPerf(b2gPerfDir, gaiaRev, geckoRev):
  print "\nRunning B2g Perf"
  subprocess.call(["adb", "forward", "tcp:2828", "tcp:2828"])
  results = {}

  for test in GAIA_APPS_TO_TEST:
    RunStartupTest(test, results, gaiaRev, geckoRev)

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
  startupTimes = RunB2GPerf(B2G_PERF_DIR, gaiaRev, geckoRev)
  #ReportResults(startupTimes)

Main()
