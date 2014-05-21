#!/bin/bash

source config.txt
CURRENT_DIR=`pwd`

cd $GAIA_DIR
git pull -u

cd $CURRENT_DIR

python main.py
