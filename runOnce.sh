#!/bin/bash

source config.txt
CURRENT_DIR=`pwd`

CheckReqs()
{
  if [ ! -d $GAIA_DIR ]
  then
    echo "Could not find GAIA directory in $GAIA_DIR"
    echo "Check config.txt please"
    exit 1
  fi

  if [ ! -d $GECKO_DIR ]
  then
    echo "Could not find GECKO Directory in $GECKO_DIR"
    echo "Check config.txt please"
    exit 1
  fi

  b2gperf &> /dev/null
  if [ $? -ne 0 ]
  then
    echo "Could not find b2g perf. Run installReqs.sh"
    exit 1
  fi
}

MoveHead()
{
  echo "Moving forward one commit"
  cd $GAIA_DIR
  git fetch
  git checkout master

  CURRENT_REVISION=`git rev-parse HEAD`
  REMOTE_REVISION=`git rev-parse origin/master`
  NEXT_COMMIT=`git log --format='%H' $CURRENT_REVISION..$REMOTE_REVISION --first-parent | tail -1`

  echo "Current Revision: " $CURRENT_REVISION
  echo "Remote Revision: " $REMOTE_REVISION
  echo "Next commit: " $NEXT_COMMIT

  if [ "$CURRENT_REVISION" = "$REMOTE_REVISION" ]
  then
    echo "Already at tip. Done"
  else
    echo "Moving to $NEXT_COMMIT"
    git reset --hard $NEXT_COMMIT
    if [ $? -ne 0 ]
    then
      echo "Could not move forward one commit"
    fi
  fi # end at next commit
}

RunScript()
{
  echo "Running Python Script"
  cd $CURRENT_DIR
  python main.py
  if [ $? -ne 0 ]
  then
    echo "Could not successfully test gaia. stopping"
    exit 1
  fi
}

CheckReqs
MoveHead
RunScript
