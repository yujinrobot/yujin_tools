###############################################################################
# Family : generic
# Platform : native
###############################################################################

# Some useful custom variables that uniquely define this platform module
set(PLATFORM_FAMILY "generic" CACHE STRING "Platform family, usually referring to intel/arm etc.")
set(PLATFORM_NAME "native" CACHE STRING "Platform name, usually referring to the cpu architecture.")

# Flags
# See here http://en.gentoo-wiki.com/wiki/Safe_Cflags for cpu type.
set(PLATFORM_CXX_FLAGS "-march=native -pipe" CACHE STRING "Compile flags specific to this platform.")
set(PLATFORM_LINK_FLAGS "" CACHE STRING "Link flags specific to this platform.")
