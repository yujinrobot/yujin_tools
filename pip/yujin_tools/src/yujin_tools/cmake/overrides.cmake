# Cmake is a bastard.
#
# You can define neither CMAKE_CXX_FLAGS or CMAKE_CXX_FLAGS_INIT in the cache. They just
# get emptied by the cmake platform and compiler modules. 
#
# Workaround is to set CMAKE_USER_MAKE_RULES_OVERRIDE to an override file (this file) and
# configure things from your own cached variables.
#
# We pick up anything residing in WINROS_CXX_FLAGS_INIT and append them.
set(CMAKE_CXX_FLAGS_INIT "${CMAKE_CXX_FLAGS_INIT} ${YUJIN_CXX_FLAGS_INIT}")