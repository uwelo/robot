VERSION := latest

all: framework hub firefox chrome

build: all

framework:
	cd ./framework && ./generate.sh $(VERSION)

hub:
	cd ./hub && ./generate.sh $(VERSION)

firefox:
	cd ./nodes/firefox && ./generate.sh $(VERSION)

chrome:
	cd ./nodes/chrome && ./generate.sh $(VERSION)

.PHONY: all build framework hub firefox chrome
