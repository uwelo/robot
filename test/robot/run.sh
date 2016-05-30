#!/bin/bash
cmd="/opt/robot/bin/run-tests.py -r http://hub:4444/wd/hub"
if test $1 == ''; then
  /opt/robot/bin/run-tests.py -h
else
  eval $cmd "$@"
fi
