#!/bin/bash
VERSION=$1

echo FROM uweloydl/robot-base:$VERSION > ./Dockerfile
cat ../Dockerfile.node.txt >> ./Dockerfile
cat ./Dockerfile.chrome.txt >> ./Dockerfile
