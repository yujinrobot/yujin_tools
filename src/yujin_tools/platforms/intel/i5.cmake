###############################################################################
# Family : intel
# Platform : i5
###############################################################################

# Some useful custom variables that uniquely define this platform module
set(PLATFORM_FAMILY "intel" CACHE STRING "Platform family, usually referring to intel/arm etc.")
set(PLATFORM_NAME "i5" CACHE STRING "Platform name, usually referring to the cpu architecture.")

# Flags
set(PLATFORM_CXX_FLAGS "-march=core2 -mfpmath=sse -msse4 -pipe -mcx16 -mmmx -mpopcnt -msahf" CACHE STRING "Compile flags specific to this platform.")
set(PLATFORM_LINK_FLAGS "" CACHE STRING "Link flags specific to this platform.")
