###############################################################################
# Family : generic
# Platform : vanilla
###############################################################################
#
# This is a special platform configuration in as much as its not special, just
# represents empty defaults.
#
# Some useful custom variables that uniquely define this platform module
set(PLATFORM_FAMILY "generic" CACHE STRING "Platform family, usually referring to intel/arm etc.")
set(PLATFORM_NAME "vanilla" CACHE STRING "Platform name, usually referring to the cpu architecture.")

# Flags
set(PLATFORM_CXX_FLAGS "" CACHE STRING "Compile flags specific to this platform.")
set(PLATFORM_LINK_FLAGS "" CACHE STRING "Link flags specific to this platform.")
