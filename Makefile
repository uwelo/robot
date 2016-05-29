VERSION := latest

all: base framework hub firefox chrome

build: all

base:
	cd ./base \
	&& docker build -t uweloydl/robot-base .

framework:
	cd ./framework && ./generate.sh $(VERSION) \
	&& docker build -t uweloydl/robot-framework .

hub:
	cd ./hub && ./generate.sh $(VERSION) \
	&& docker build -t uweloydl/robot-hub .

firefox:
	cd ./nodes/firefox && ./generate.sh $(VERSION) \
	&& docker build -t uweloydl/robot-firefox .

chrome:
	cd ./nodes/chrome && ./generate.sh $(VERSION) \
	&& docker build -t uweloydl/robot-chrome .

.PHONY: all build base framework hub firefox chrome
