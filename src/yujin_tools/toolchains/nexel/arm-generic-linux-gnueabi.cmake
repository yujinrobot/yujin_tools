# 
# SET(CMAKE_C_COMPILER    /opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/arm-generic-linux-gnueabi-gcc)
# SET(CMAKE_CXX_COMPILER  /opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/arm-generic-linux-gnueabi-g++)
# SET(CMAKE_LINKER        /opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/arm-generic-linux-gnueabi-ld)
# SET(CMAKE_NM            /opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/arm-generic-linux-gnueabi-nm)
# SET(CMAKE_OBJCOPY       /opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/arm-generic-linux-gnueabi-objcopy)
# SET(CMAKE_OBJDUMP       /opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/arm-generic-linux-gnueabi-objdump)
# SET(CMAKE_RANLIB        /opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/arm-generic-linux-gnueabi-ranlib)

###############################################################################
# Family : nexel_touched
# Tuple : arm-generic-linux-gnueabli
# Sysroot : /usr/arm-none-linux-gnueabi/libc
###############################################################################

# Some useful custom variables that uniquely define this toolchain module
set(TOOLCHAIN_FAMILY "nexel_touched")
set(TOOLCHAIN_TUPLE "arm-generic-linux-gnueabi" CACHE STRING "Toolchain signature identifying cpu-vendor-platform-clibrary.")
set(TOOLCHAIN_SYSROOT "/opt/crosstools/arm-eabi-4.3.2-glibc-2.9/${TOOLCHAIN_TUPLE}/sys-root" CACHE STRING "Root of the target development environment (libraries, headers etc).")
#set(TOOLCHAIN_INSTALL_PREFIX "${TOOLCHAIN_SYSROOT}/usr" CACHE STRING "Preferred install location when using the toolchain.")
set(TOOLCHAIN_NAME_PREFIX "/opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/${TOOLCHAIN_TUPLE}-")

# Now the cmake variables
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR "arm")
set(CMAKE_C_COMPILER    /opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/${TOOLCHAIN_TUPLE}-gcc) # Make sure these are in your PATH
set(CMAKE_CXX_COMPILER  /opt/crosstools/arm-eabi-4.3.2-glibc-2.9/bin/${TOOLCHAIN_TUPLE}-g++)
set(CMAKE_FIND_ROOT_PATH ${TOOLCHAIN_SYSROOT} CACHE STRING "Cmake search variable for finding libraries/headers.")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER) # Don't search for programs in sysroot
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)  # Headers and libs from sysroot only
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# Hide from cache's front page
MARK_AS_ADVANCED(CMAKE_GENERATOR CMAKE_FIND_ROOT_PATH CMAKE_TOOLCHAIN_FILE TOOLCHAIN_FAMILY TOOLCHAIN_TUPLE TOOLCHAIN_SYSROOT)
