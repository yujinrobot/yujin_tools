###############################################################################
# Family : arm
# Platform : arm1176jzf-s
# Notes: use with armel compilers.
###############################################################################

# Some useful custom variables that uniquely define this platform module
set(PLATFORM_FAMILY "arm" CACHE STRING "Platform family, usually referring to intel/arm etc.")
set(PLATFORM_NAME "arm1176jzf-s" CACHE STRING "Platform name, usually referring to the cpu architecture.")

# Flags
set(PLATFORM_CXX_FLAGS "-march=armv6 -mtune=arm1176jzf-s -pipe -mfloat-abi=softfp -mfpu=vfp" CACHE STRING "Compile flags specific to this platform.")
set(PLATFORM_LINK_FLAGS "" CACHE STRING "Link flags specific to this platform.")
