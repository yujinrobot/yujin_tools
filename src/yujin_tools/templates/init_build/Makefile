# Used to quick start builds with ros-catkin on linux systems.

PWD:=$(shell pwd)

# Location of sources relative to BUILDSPACE
SOURCE="%(rel_source_dir)s"

# Configure with a toolchain module
TOOLCHAIN=%(toolchain)s
#TOOLCHAIN=-DCMAKE_TOOLCHAIN_FILE=./src/dfsadf

# Path to catkin_make (we're using yujin_make module till catkin 0.5.65 hits debs)
# CATKIN_MAKE=%(catkin_make)s)

# Python path to catkin's python module (we're using yujin_make module till catkin 0.5.65 hits debs)
# CATKIN_PYTHON_PATH=%(catkin_python_path)s)

# Initialise the cache with global variables (usually use for platform specific variables)
CACHE=-C${PWD}/config.cmake

# User override file, used to set global compiler flags set in config.cmake
OVERRIDE="-DCMAKE_USER_MAKE_RULES_OVERRIDE:STRING=%(override)s"

# Number of jobs for installs.
JOBS=5

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
	mkdir -p ${PWD}/build
	cd build; cmake ${TOOLCHAIN} ${CACHE} ../${SOURCE}

ccmake:
	cd build; ccmake .

# Note that this defaults to ROS_PARALLEL_JOBS and falls back to no. of cores for parallelisation	
build: 
	yujin_make --source=${SOURCE} --cmake-args ${TOOLCHAIN} ${CACHE}

# Note that this defaults to ROS_PARALLEL_JOBS and falls back to no. of cores for parallelisation	
rebuild: 
	yujin_make --force-cmake --source=${SOURCE} --cmake-args ${TOOLCHAIN} ${CACHE}

# No parallelisation for this
install:
	cd build; make -j5 install
 
# No parallelisation for this
tests:
	cd build; make -j5 tests

run_tests:
	cd build; make run_tests

clean:
	rm -rf build
	rm -rf devel
	rm -rf install

.PHONY: build install ccmake cmake tests clean
