#!/bin/bash
echo "Running updating b2gperf reqs. This will ask for sudo. Please provide the sudo password."
sudo ./installReqs.sh
if [ $? -ne 0 ]
then
  echo "Could not update b2g perf requirements. Please run installReqs.sh manually and see the error"
  exit 1
fi

# Runs forever!
while true
do
  ./runOnce.sh
  sleep 1
done
