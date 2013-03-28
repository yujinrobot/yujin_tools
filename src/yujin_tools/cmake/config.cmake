###########################
# Parameterised Variables
###########################
set(UNDERLAY_ROOTS "%(config_underlays)s" CACHE PATH "Semi-colon separated list of underlay roots.")

###########################
# CMake
###########################
# Be careful changing the build type - the rosdeps are typically 
# built Release or RelWithDebInfo. Mixed mode building typically does
# not work with msvc, so Debug won't work against rosdeps built as stated
# above. 
# If you do want to build Debug:
# - compile the rosdeps in debug mode
# - call the visual studio shell script (usually in src/setup.bat) in debug mode
# - make sure any projects on top are built in debug mode also.
set(CMAKE_BUILD_TYPE %(config_build_type)s CACHE STRING "Build mode type.")
set(CMAKE_INSTALL_PREFIX %(config_install_prefix)s CACHE PATH "Install root location.")
set(CMAKE_PREFIX_PATH "${UNDERLAY_ROOTS}" CACHE PATH "semi-colon separated software/ros workspace paths.")
# We use CMAKE_USER_MAKE_RULES_OVERRIDE to configure CMAKE_CXX_FLAGS_INIT ()
set(YUJIN_CXX_FLAGS_INIT "" CACHE STRING "Initial flags that get passed to CMAKE_CXX_FLAGS via the cmake override file.")
set(CMAKE_USER_MAKE_RULES_OVERRIDE "%(config_override_file)s" CACHE PATH "User override file for setting global compiler flags.")

###########################
# Catkin
###########################
# Excluding or including packages
#set(CATKIN_BLACKLIST_PACKAGES "" CACHE STRING "List of ';' separated packages to exclude")
#set(CATKIN_WHITELIST_PACKAGES "" CACHE STRING "List of ';' separated packages to build (must be a complete list)")
set(CATKIN_DEVEL_PREFIX "devel")

###########################
# Boost
###########################
set(Boost_DEBUG FALSE CACHE BOOL "Debug boost.")
set(Boost_DETAILED_FAILURE_MSG FALSE CACHE BOOL "Detailed failure reports from boost.")