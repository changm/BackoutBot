#!/bin/bash
easy_install gitpython
if [ $? -ne 0 ]
then
  echo "Could not install gitpython. Exiting"
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
