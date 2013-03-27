# Used to quick start builds with ros-catkin on linux systems.

PWD:=$(shell pwd)

# Use this to set a different workspace directory, e.g.
BUILD=build

# Location of sources relative to BUILDSPACE
SOURCE="%(rel_source_dir)s"

# Full path to catkin_make
CATKIN_MAKE="%(catkin_make)s"

# Configure with a toolchain module
TOOLCHAIN=%(toolchain)s
#TOOLCHAIN=-DCMAKE_TOOLCHAIN_FILE=./src/dfsadf

# Initialise the cache with global variables (usually use for platform specific variables)
CACHE=-C "config.cmake"

# User override file, used to set global compiler flags set in config.cmake
OVERRIDE="-DCMAKE_USER_MAKE_RULES_OVERRIDE:STRING=%(override)s"

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
	mkdir -p ${PWD}/${BUILD}
	cd ${BUILD}; cmake ${TOOLCHAIN} ${CACHE} ../${SOURCE}

ccmake:
	cd ${BUILD}; ccmake .

# Note that this defaults to ROS_PARALLEL_JOBS and falls back to no. of cores for parallelisation	
build: 
	${CATKIN_MAKE} --directory=${PWD} --source=${SOURCE} --build=${BUILD} ${TOOLCHAIN} ${CACHE}

# Note that this defaults to ROS_PARALLEL_JOBS and falls back to no. of cores for parallelisation	
rebuild: 
	${CATKIN_MAKE} --force-cmake --directory=${PWD} --source=${SOURCE} --build=${BUILD} ${TOOLCHAIN} ${CACHE}

# No parallelisation for this
install:
	cd ${BUILD}; make -j5 install
 
# No parallelisation for this
tests:
	cd ${BUILD}; make -j5 tests

run_tests:
	cd ${BUILD}; make run_tests

clean:
	rm -rf ${BUILD}
	rm -rf devel
	rm -rf install

.PHONY: ${BUILD} install ccmake cmake tests clean
