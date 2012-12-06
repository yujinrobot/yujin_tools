# Used to quick start builds with ros-catkin on linux systems.

PWD:=$(shell pwd)

# Use this to set a different workspace directory, e.g.
#WORKSPACE="--directory=./arm-linux-gnu"
WORKSPACE=${PWD}

# Build directory name, relative to workspace
BUILD="build"

# Location of sources relative to workspace
SOURCE="../src"

# Location of installation directory
#CMAKE_INSTALL_PREFIX:=${PWD}/install
INSTALL="-DCMAKE_INSTALL_PREFIX=${WORKSPACE}/install"

# Configure with a toolchain module
TOOLCHAIN=
#TOOLCHAIN=-DCMAKE_TOOLCHAIN_FILE=./src/dfsadf

# Initialise the cache with global variables (usually use for platform specific variables)
PLATFORM=
#PLATFORM="-C ./src/xsfdasdf"

# Blacklist certain packages
BLACKLIST=
#BLACKLIST="-DCATKIN_BLACKLIST_PACKAGES=cslam_qt_monitor;cslam_web_monitor"

help:
	@echo ""
	@echo "Usage: make <target>"
	@echo "   cmake:     force a cmake reconfiguration."
	@echo "   ccmake:    view/modify cmake variables in an existing build directory."
	@echo "   build:     compile sources"
	@echo "   install:   install into target directory"
	@echo "   tests:     build tests"
	@echo "   clean:     remove all build, devel and install directories."
	@echo ""

cmake:
	mkdir -p ${WORKSPACE}/${BUILD}
	cd ${WORKSPACE}/${BUILD}; cmake ${TOOLCHAIN} ${PLATFORM} ${INSTALL} ${BLACKLIST} ../${SOURCE}

ccmake:
	cd ${WORKSPACE}/${BUILD}; ccmake .
	
build: 
	catkin_make --directory=${WORKSPACE} --source=${SOURCE} --build=${BUILD} ${TOOLCHAIN} ${PLATFORM} ${INSTALL} ${BLACKLIST}; \

install:
	cd ${WORKSPACE}/${BUILD}; make -j5 install
 
tests:
	cd ${WORKSPACE}/${BUILD}; make -j5 tests

clean:

	rm -rf build
	rm -rf devel
	rm -rf install

.PHONY: build install ccmake cmake tests clean
