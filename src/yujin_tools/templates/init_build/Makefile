# Used to quick start builds with ros-catkin on linux systems.

PWD:=$(shell pwd)

# Use this to set a different workspace directory, e.g.
#WORKSPACE="--directory=./arm-linux-gnu"
WORKSPACE=${PWD}

# Build directory name, relative to workspace
BUILD="build"

# Location of sources relative to workspace
SOURCE="%(source_dir)s"

# Location of installation directory
INSTALL="-DCMAKE_INSTALL_PREFIX=%(install_prefix)s"

# Underlays
UNDERLAYS="-DCMAKE_PREFIX_PATH=%(underlays)s"

# Configure with a toolchain module
TOOLCHAIN=%(toolchain)s
#TOOLCHAIN=-DCMAKE_TOOLCHAIN_FILE=./src/dfsadf

# Initialise the cache with global variables (usually use for platform specific variables)
PLATFORM=%(platform)s
#PLATFORM="-C ./src/xsfdasdf"

# Blacklist certain packages
BLACKLIST=
#BLACKLIST="-DCATKIN_BLACKLIST_PACKAGES=cslam_qt_monitor;cslam_web_monitor"

# Development space relative to workspace
DEVEL="-DCATKIN_DEVEL_PREFIX=./devel"

# Build mode - DebugWithRelSymbols, Release
BUILD_TYPE="-DCMAKE_BUILD_TYPE=%(build_type)s"

help:
	@echo ""
	@echo "Usage: make <target>"
	@echo "   cmake:     cmake (re)configuration only, no compiling."
	@echo "   ccmake:    view/modify cmake variables in an existing build directory."
	@echo "   build:     compile sources"
	@echo "   rebuild:   force a redo of cmake configuration and rebuild"
	@echo "   install:   install into target directory"
	@echo "   tests:     build tests"
	@echo "   run_tests: run tests"
	@echo "   clean:     remove all build, devel and install directories."
	@echo ""
	@echo "Most common targets will be build, rebuild and clean."
	@echo ""

cmake:
	mkdir -p ${WORKSPACE}/${BUILD}
	cd ${WORKSPACE}/${BUILD}; cmake ${BUILD_TYPE} ${DEVEL} ${UNDERLAYS} ${TOOLCHAIN} ${PLATFORM} ${INSTALL} ${BLACKLIST} ../${SOURCE}

ccmake:
	cd ${WORKSPACE}/${BUILD}; ccmake .

# Note that this defaults to ROS_PARALLEL_JOBS and falls back to no. of cores for parallelisation	
build: 
	. /opt/ros/groovy/setup.sh; \
	catkin_make --directory=${WORKSPACE} --source=${SOURCE} --build=${BUILD} ${BUILD_TYPE} ${UNDERLAYS} ${TOOLCHAIN} ${PLATFORM} ${INSTALL} ${BLACKLIST}

# Note that this defaults to ROS_PARALLEL_JOBS and falls back to no. of cores for parallelisation	
rebuild: 
	. /opt/ros/groovy/setup.sh; \
	catkin_make --force-cmake --directory=${WORKSPACE} --source=${SOURCE} --build=${BUILD} ${BUILD_TYPE} ${UNDERLAYS} ${TOOLCHAIN} ${PLATFORM} ${INSTALL} ${BLACKLIST}

# No parallelisation for this
install:
	cd ${WORKSPACE}/${BUILD}; make -j5 install
 
# No parallelisation for this
tests:
	cd ${WORKSPACE}/${BUILD}; make -j5 tests

run_tests:
	cd ${WORKSPACE}/${BUILD}; make run_tests

clean:
	rm -rf build
	rm -rf devel
	rm -rf install

.PHONY: build install ccmake cmake tests clean
