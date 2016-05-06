#!/bin/bash
VERSION=$1

cp ../base/entry.sh entry.sh
cp ../base/functions.sh functions.sh

echo FROM uweloydl/robot-base:$VERSION > ./Dockerfile
cat ../base/Dockerfile.node.txt >> ./Dockerfile
cat ./Dockerfile.firefox.txt >> ./Dockerfile
