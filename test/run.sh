#!/bin/bash
cmd="docker run -v $(pwd)/robot/:/opt/robot uweloydl/robot-framework"
echo $1
if test $1 == ''; then
  eval $cmd -h
else
  eval $cmd "$@"
fi

#docker run -v ./robot/:/opt/robot uweloydl/robot-framework \
#  --no-proxy -r http://172.17.0.1:4444/wd/hub -b ff -t tests
