###############################################################################
# Family : intel
# Platform : atomn270
###############################################################################

# Some useful custom variables that uniquely define this platform module
set(PLATFORM_FAMILY "intel" CACHE STRING "Platform family, usually referring to intel/arm etc.")
set(PLATFORM_NAME "atomn270" CACHE STRING "Platform name, usually referring to the cpu architecture.")

# Flags
# Refer to http://en.gentoo-wiki.com/wiki/Safe_Cflags/Intel for cpu type.
# Refer to http://en.gentoo-wiki.com/wiki/Safe_Cflags#General_Information_on_CFLAGS. 
# From gcc 4.5+ we can start using -march=atom -mtune=atom
set(PLATFORM_CXX_FLAGS "-march=core2 -mtune=generic -pipe -fomit-frame-pointer -mfpmath=sse -mmmx -mssse3" CACHE STRING "Compile flags specific to this platform.")
set(PLATFORM_LINK_FLAGS "" CACHE STRING "Link flags specific to this platform.")
