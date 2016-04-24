#!/bin/bash
VERSION=$1

echo FROM uweloydl/robot-base:$VERSION > ./Dockerfile
cat ./Dockerfile.robot.txt >> ./Dockerfile
