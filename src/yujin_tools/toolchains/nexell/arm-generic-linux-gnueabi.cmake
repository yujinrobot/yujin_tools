# 
# SET(CMAKE_C_COMPILER    ${TOOLCHAIN_ROOT}/bin/arm-generic-linux-gnueabi-gcc)
# SET(CMAKE_CXX_COMPILER  ${TOOLCHAIN_ROOT}/bin/arm-generic-linux-gnueabi-g++)
# SET(CMAKE_LINKER        ${TOOLCHAIN_ROOT}/bin/arm-generic-linux-gnueabi-ld)
# SET(CMAKE_NM            ${TOOLCHAIN_ROOT}/bin/arm-generic-linux-gnueabi-nm)
# SET(CMAKE_OBJCOPY       ${TOOLCHAIN_ROOT}/bin/arm-generic-linux-gnueabi-objcopy)
# SET(CMAKE_OBJDUMP       ${TOOLCHAIN_ROOT}/bin/arm-generic-linux-gnueabi-objdump)
# SET(CMAKE_RANLIB        ${TOOLCHAIN_ROOT}/bin/arm-generic-linux-gnueabi-ranlib)

###############################################################################
# Family : nexell
# Tuple : arm-generic-linux-gnueabli
# Sysroot : /usr/arm-none-linux-gnueabi/libc
###############################################################################

# Some useful custom variables that uniquely define this toolchain module
set(TOOLCHAIN_FAMILY "nexell" CACHE STRING "Convenient grouping identifier for collections of toolchains (e.g. ubuntu, nexell, sourcery).")
set(TOOLCHAIN_TUPLE "arm-generic-linux-gnueabi" CACHE STRING "Toolchain signature identifying cpu-vendor-platform-clibrary.")
set(TOOLCHAIN_ROOT "/opt/nexell/toolchain/arm-eabi-4.3.2-glibc-2.9" CACHE STRING "Root of the installed toolchain")
set(TOOLCHAIN_SYSROOT "${TOOLCHAIN_ROOT}/${TOOLCHAIN_TUPLE}/sys-root" CACHE STRING "Root of the target development environment (libraries, headers etc).")
#set(TOOLCHAIN_INSTALL_PREFIX "${TOOLCHAIN_SYSROOT}/usr" CACHE STRING "Preferred install location when using the toolchain.")
set(TOOLCHAIN_NAME_PREFIX "${TOOLCHAIN_ROOT}/bin/${TOOLCHAIN_TUPLE}-")

# Now the cmake variables
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR "arm")
set(CMAKE_C_COMPILER    ${TOOLCHAIN_ROOT}/bin/${TOOLCHAIN_TUPLE}-gcc) # Make sure these are in your PATH
set(CMAKE_CXX_COMPILER  ${TOOLCHAIN_ROOT}/bin/${TOOLCHAIN_TUPLE}-g++)
set(CMAKE_FIND_ROOT_PATH ${TOOLCHAIN_SYSROOT} CACHE STRING "Cmake search variable for finding libraries/headers.")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER) # Don't search for programs in sysroot
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)  # Headers and libs from sysroot only
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# Hide from cache's front page
MARK_AS_ADVANCED(CMAKE_GENERATOR CMAKE_FIND_ROOT_PATH CMAKE_TOOLCHAIN_FILE TOOLCHAIN_FAMILY TOOLCHAIN_TUPLE TOOLCHAIN_SYSROOT)
