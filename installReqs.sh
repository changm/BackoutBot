#!/bin/bash
easy_install gitpython
if [ $? -ne 0 ]
then
  echo "==== OH NOES!!. Please read below ==="
  echo "Could not install gitpython. Did you get a permission denied? Run me with sudo!."
  echo "I also need internet. Make sure I have internet plz. kthxbai"
  echo
  echo "Exiting"
  exit 1
fi

pip install b2gperf
if [ $? -ne 0 ]
then
  echo "Could not install b2g perf. Exiting"
  exit 1
fi

pip install --upgrade b2gperf
if [ $? -ne 0 ]
then
  echo "Could not upgrade b2g perf. Exiting"
  exit 1
fi

pip install python-hglib
if [ $? -ne 0 ]
then
  echo "Could not install python hglib. Exiting"
  exit 1
fi

echo
echo "==== Finished Installing Reqs for Backout Bot ===="
