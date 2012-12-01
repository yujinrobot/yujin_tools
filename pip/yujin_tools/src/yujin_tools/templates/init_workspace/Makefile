# Used to quick start builds with ros-catkin on linux systems.

PWD:=$(shell pwd)

# Use this to set a different workspace directory, e.g.
#WORKSPACE="--directory=./arm-linux-gnu"
WORKSPACE="./"

# Build directory name, relative to workspace
BUILD="build"

# Location of sources relative to workspace
SOURCE="./src"

#CMAKE_INSTALL_PREFIX:=${PWD}/install
INSTALL="-DCMAKE_INSTALL_PREFIX=install"

# Configure with a toolchain module
TOOLCHAIN=
#TOOLCHAIN=-DCMAKE_TOOLCHAIN_FILE=./src/dfsadf

# Initialise the cache with global variables (usually use for platform specific variables)
PLATFORM=
#PLATFORM="-C ./src/xsfdasdf"

help:
	@echo ""
	@echo "Usage: make <target>"
	@echo "   ccmake:    view/modify cmake variables in an existing build directory."
	@echo "   build:     compile sources"
	@echo "   install:   install into target directory"
	@echo "   tests:     build tests"
	@echo "   clean:     remove all build, devel and install directories."
	@echo ""

cmake:
	cd ${WORKSPACE}/${BUILD}; cmake .

ccmake:
	cd ${WORKSPACE}/${BUILD}; ccmake .
	
build: 
	catkin_make --directory=${WORKSPACE} --source=${SOURCE} --build=${BUILD} ${TOOLCHAIN} ${PLATFORM} ${INSTALL} --force-cmake

install:
	cd ${WORKSPACE}/${BUILD}; make -j5 install
 
tests:
	cd ${WORKSPACE}/${BUILD}; make -j5 tests

clean:
	rm -rf build
	rm -rf devel
	rm -rf install

.PHONY: clean
