#!/bin/bash

docker run -v ./robot/:/opt/robot uweloydl/robot-framework \
  --no-proxy -r http://172.17.0.1:4444/wd/hub -b ff -t tests
