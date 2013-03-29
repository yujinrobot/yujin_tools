###############################################################################
# Family : ubuntu
# Tuple : i586-mingw32msvc
# Sysroot : /usr/i586-mingw32msvc
###############################################################################

# Some useful custom variables that uniquely define this toolchain module
set(TOOLCHAIN_FAMILY "ubuntu")
set(TOOLCHAIN_TUPLE "i586-mingw32msvc" CACHE STRING "Toolchain signature identifying cpu-vendor-platform-clibrary.")
set(TOOLCHAIN_SYSROOT "/usr/${TOOLCHAIN_TUPLE}" CACHE STRING "Root of the target development environment (libraries, headers etc).")
set(TOOLCHAIN_INSTALL_PREFIX "${TOOLCHAIN_SYSROOT}" CACHE STRING "Preferred install location when using the toolchain.")

# Now the cmake variables
set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_C_COMPILER   ${TOOLCHAIN_TUPLE}-gcc) # Make sure these are in your PATH
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_TUPLE}-g++)
set(CMAKE_FIND_ROOT_PATH ${TOOLCHAIN_SYSROOT} CACHE STRING "Cmake search variable for finding libraries/headers.")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER) # Don't search for programs in sysroot
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)  # Headers and libs from sysroot only
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

###############################
# Mingw Ecosystem is Static
###############################
# TODO - these need to be updated for groovy
#set(ROS_BUILD_STATIC_EXES true)
#set(ROS_BUILD_SHARED_EXES false)
#set(ROS_BUILD_STATIC_LIBS true)
#set(ROS_BUILD_SHARED_LIBS false)

# Hide from cache's front page
MARK_AS_ADVANCED(CMAKE_GENERATOR CMAKE_FIND_ROOT_PATH CMAKE_TOOLCHAIN_FILE TOOLCHAIN_FAMILY TOOLCHAIN_TUPLE TOOLCHAIN_SYSROOT)
                                                                                                