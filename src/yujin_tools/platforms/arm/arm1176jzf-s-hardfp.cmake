###############################################################################
# Family : arm
# Platform : arm1176jzf-s with hardfp
# Notes: use with armel compilers.
###############################################################################

# Some useful custom variables that uniquely define this platform module
set(PLATFORM_FAMILY "arm" CACHE STRING "Platform family, usually referring to intel/arm etc.")
set(PLATFORM_NAME "arm1176jzf-s" CACHE STRING "Platform name, usually referring to the cpu architecture.")

# Flags
set(PLATFORM_CXX_FLAGS "-march=armv6 -mtune=arm1176jzf-s -pipe -mfloat-abi=hard -mfpu=vfp" CACHE STRING "Compile flags specific to this platform.")
set(PLATFORM_LINK_FLAGS "" CACHE STRING "Link flags specific to this platform.")

# Custom software settings
set(ECL_EIGEN_IS_INTERNAL_3_2_1 TRUE CACHE BOOL "Use ecls internal eigen.")
# Nanomsg - disable it's support for gcc builtins
set(NN_DISABLE_ATOMIC_GCC_BUILTINS TRUE CACHE BOOL "Disable atomic gcc builtins.")
# Disable opencv debugging on the dslam repo
set(DSLAM_ENABLE_OPENCV FALSE CACHE BOOL "Enable opencv debugging on the dslam repo.")