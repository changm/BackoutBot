#!/bin/bash

source config.txt
CURRENT_DIR=`pwd`

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

MoveHead

echo "Running Python Script"
cd $CURRENT_DIR
python main.py
