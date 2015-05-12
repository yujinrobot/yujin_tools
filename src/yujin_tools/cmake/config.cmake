
###############################################################################
# Build Configuration
###############################################################################

###########################
# Parameterised Variables
###########################
set(UNDERLAY_ROOTS "%(config_underlays)s" CACHE PATH "Semi-colon separated list of underlay roots.")
set(YUJIN_DOC_PREFIX "%(config_doc_prefix)s" CACHE PATH "Document root location")

###########################
# CMake
###########################
set(CMAKE_VERBOSE_MAKEFILE ON CACHE BOOL "Verbosity in the makefile compilations.")
set(CMAKE_BUILD_TYPE %(config_build_type)s CACHE STRING "Build mode type.")
set(CMAKE_INSTALL_PREFIX "%(config_install_prefix)s" CACHE PATH "Install root location.")
set(CMAKE_PREFIX_PATH "${UNDERLAY_ROOTS}" CACHE PATH "semi-colon separated software/ros workspace paths.")
# We use CMAKE_USER_MAKE_RULES_OVERRIDE to configure CMAKE_CXX_FLAGS_INIT ()
set(YUJIN_CXX_FLAGS_INIT "${PLATFORM_CXX_FLAGS}" CACHE STRING "Initial flags that get passed to CMAKE_CXX_FLAGS via the cmake override file.")
set(CMAKE_USER_MAKE_RULES_OVERRIDE "%(config_override_file)s" CACHE PATH "User override file for setting global compiler flags.")

###########################
# Catkin
###########################
# Excluding or including packages
#set(CATKIN_BLACKLIST_PACKAGES "" CACHE STRING "List of ';' separated packages to exclude")
#set(CATKIN_WHITELIST_PACKAGES "" CACHE STRING "List of ';' separated packages to build (must be a complete list)")
set(CATKIN_DEVEL_PREFIX "%(config_devel)s" CACHE PATH "Relative location of the devel space [devel]")

###########################
# Boost
###########################
set(Boost_DEBUG FALSE CACHE BOOL "Debug boost.")
set(Boost_DETAILED_FAILURE_MSG FALSE CACHE BOOL "Detailed failure reports from boost.")
