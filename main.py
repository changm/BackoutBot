import os
import git
import subprocess
import os
import hglib
import re
import sys
import time

GECKO_DIR=""
GAIA_DIR=""
RESULTS_FILE="results.txt"
LOG_FILE="results.log.txt"
REGRESSIONS_FILE="regressions.txt"

# Need to get a sd card to test
# These apps are case sensitive names
GAIA_APPS_TO_TEST=["Settings", "Phone", "Camera", "Email", "Contacts"]

# Tuples from results are in the order of
# (median, mean, std dev, gaia rev, gecko rev)
def GetMedian(results):
  medianIndex = 0
  return results[medianIndex]

def GetMean(results):
  meanIndex = 1
  return results[meanIndex]

def GetStdDev(results):
  stdDevIndex = 2
  return results[stdDevIndex]

def GetGaiaRev(results):
  gaiaRevIndex = 3
  return str(results[gaiaRevIndex])

def GetGeckoRev(results):
  geckoRevIndex = 4
  return str(results[geckoRevIndex])

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
  currentDir = os.getcwd()
  os.chdir(gaiaDir)
  env = os.environ

  # ignore first time user. CAn't do this because b2gperf
  # can't unlock the homescreen, so we have to have FTU up. sad
  # env["NOFTU"] = "1"

  subprocess.call(["make", "reset-gaia"])

  print "Flashed Gaia, rebooting device.... Sleeping for 2 minutes"
  subprocess.call(["adb", "reboot"])
  time.sleep(120)
  os.chdir(currentDir)

# Returns a tuple with (median, mean, stdDev)
def ExtractStartupData(resultString):
  # Our string looks like: Results for Settings, cold_load_time: median:1945, mean:2008, std: 97, max:2146, min:1934, all:2146,1934,1945
  # strip out the median, mean, and std deviatoin numbers. Ugly Regex sadface
  regexResults = re.search(".*median:([0-9]+).*mean:([0-9]+).*std: ([0-9]+).*", resultString)
  if (regexResults == None):
    print "Regex Could not find any start up data. Exiting"
    print "Result string is: " + str(resultString)
    return (1000, 1000, 100)
    #sys.exit(1)

  return regexResults.groups()

def GetFileName(appName):
  global RESULTS_FILE
  return appName + "." + RESULTS_FILE

def WriteTestResults(appName, resultString, gaiaRevision, geckoRevision):
  fileName = GetFileName(appName)
  file = open(fileName, 'w')
  lines = []
  lines.append("Results for: " + str(appName) + "\n")
  lines.append("Gaia Revision: " + str(gaiaRevision) + "\n")
  lines.append("Gecko Revision: " + str(geckoRevision) + "\n")

  lines.append(resultString)
  file.writelines(lines)
  file.flush()
  file.close()

# Return a tuple of (gaia, gecko) revisions
def GetRevisions(lines):
  gaiaRev = re.search("Gaia.*: (\w+)", lines)
  if gaiaRev:
    gaiaRev = gaiaRev.groups()[0].strip()

  geckoRev = re.search("Gecko.*: (.*)", lines)
  if geckoRev:
    geckoRev = geckoRev.groups()[0].strip()

  return (gaiaRev, geckoRev)

# Returns a tuple of (mean, median,stdDev, gaiaRev, geckoRev)
def GetLastResults(appName):
  fileName = GetFileName(appName)
  try:
    file = open(fileName, "r")
  except:
    print "Could not open results file: " + str(fileName) + ". Setting new baseline"
    return (10000, 10000, 10000, 1000, "10000:10000")

  lines = file.readlines()
  lines = "".join(lines)
  file.close()

  revisions = GetRevisions(lines)
  return ExtractStartupData(lines) + revisions

def DealWithRegression(appName, previousResults, currentResults):
  global REGRESSIONS_FILE

  previousMean = GetMean(previousResults)
  prevStdDev = GetStdDev(previousResults)

  currentMean = GetMean(currentResults)
  currentStdDev = GetStdDev(currentResults)
  print "AND WE HAVE A REGRESSION. Previous Mean: " + str(previousMean) + " current mean: " + currentMean

  try:
    file = open(REGRESSIONS_FILE, "a")
  except:
    print "Could not open regressions file"
    return

  gaiaRev = GetGaiaRev(currentResults)
  geckoRev = GetGeckoRev(currentResults)

  line = "Regression in app: " + appName + "\n"
  line += "Gaia Rev: " + gaiaRev + " Gecko Rev: " + geckoRev + "\n"
  line += "Previous mean: " + str(previousMean) + " prev std dev: " + str(prevStdDev) + "\n"
  line += "Current mean: " + str(currentMean) + " current std dev: " + str(currentStdDev) + "\n"

  file.write(line)
  file.flush()
  file.close()

def PassTest(previousResults, currentResults):
  prevMean = GetMean(previousResults)
  prevStd = GetStdDev(previousResults)

  currentMean = GetMean(currentResults)
  currentStdDev = GetStdDev(currentResults)

  print "\nPassed Tests"
  print "Current mean: " + str(currentMean) + " std dev: " + str(currentStdDev)
  print "Previous mean: " + str(prevMean) + " std dev: " + str(prevStd)

  prevGaiaRev = GetGaiaRev(previousResults)
  prevGeckoRev = GetGeckoRev(previousResults)
  print "Prev Gaia: " + str(prevGaiaRev) + "\nPrev Gecko: " + prevGeckoRev

# Each should be a tuple of (median, mean, stdDev)
def AnalyzeResults(appName, previousResults, currentResults):
  previousMean = int(GetMean(previousResults))
  previousStdDev = int(GetStdDev(previousResults))

  print "Previous std dev: " + str(previousStdDev)

  threshold = previousMean + previousStdDev
  print "Threshold is: " + str(threshold)

  currentMean = int(GetMean(currentResults))
  if (currentMean >= threshold):
    DealWithRegression(appName, previousResults, currentResults)
  else:
    PassTest(previousResults, currentResults)

def RunStartupTest(appName, results, gaiaRev, geckoRev):
  print "\nRunning b2g perf for app: " + str(appName)

  # Need the --reset, see bug 1011033
  # b2gperf does 30 iterations, but that takes too long to execute
  # 20 isn't enough to keep up with every gaia check in
  # Trying 15, might even be 10 would be good enough. Keep playing with the iteration number
  proc = subprocess.Popen(["b2gperf", "--delay=10", "--iterations=15", "--reset", str(appName)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()

  print "Output from b2g perf"
  print err

  lastResults = GetLastResults(appName)
  WriteTestResults(appName, err, gaiaRev, geckoRev)
  currentResults = ExtractStartupData(err) + (gaiaRev, geckoRev)

  AnalyzeResults(appName, lastResults, currentResults)
  return (lastResults, currentResults)

def RunB2GPerf(gaiaRev, geckoRev):
  print "\nRunning B2g Perf"
  subprocess.call(["adb", "forward", "tcp:2828", "tcp:2828"])
  results = {}

  for test in GAIA_APPS_TO_TEST:
    results[test] = RunStartupTest(test, results, gaiaRev, geckoRev)

  return results

def ReportResults(results, gaiaRev, geckoRev):
  print "\n==== Printing Results ====\n"
  print "Gaia: " + str(gaiaRev)
  print "Gecko: " + str(geckoRev) + "\n"

  for test in results:
    print "Results for test: " + test
    lastResults, currentResults = results[test]

    prevMean = GetMean(lastResults)
    prevStdDev = GetStdDev(lastResults)

    currentMean = GetMean(currentResults)
    currentStdDev = GetStdDev(currentResults)

    print "Current mean: " + str(currentMean) + " std dev: " + str(currentStdDev)
    print "Prev Mean: " + str(prevMean) + " std dev: " + str(prevStdDev)
    print ""

def WriteResults(startupTimes, gaiaRev, geckoRev):
  try:
    file = open(LOG_FILE, 'a')
  except:
    print "Could not open log file"

  revisions = "Gaia: " + str(gaiaRev) + " Gecko: " + (geckoRev) + "\n"
  file.write(revisions)

  for test in startupTimes:
    lastResults, currentResults = startupTimes[test]

    currentMedian = GetMedian(currentResults)
    currentMean = GetMean(currentResults)
    currentStdDev = GetStdDev(currentResults)

    line = "Test: " + str(test) + "\t"
    line += "Median: " + str(currentMedian) + "\t"
    line += "Mean: " + str(currentMean) + "\t"
    line += "Std Dev: " + str(currentStdDev) + "\n"
    file.write(line)

  file.flush()
  file.close()
  print "Wrote results to log: " + LOG_FILE

def Main():
  global GECKO_DIR
  global GAIA_DIR

  config = ReadConfig()
  ParseConfigs(config)
  gaiaRev = GetGaiaRevision(GAIA_DIR)
  geckoRev = GetGeckoRevision(GECKO_DIR)

  FlashGaia(GAIA_DIR)

  startupTimes = RunB2GPerf(gaiaRev, geckoRev)
  ReportResults(startupTimes, gaiaRev, geckoRev)
  WriteResults(startupTimes, gaiaRev, geckoRev)

Main()
