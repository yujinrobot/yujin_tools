##############################################################################
# Imports
##############################################################################

import os
import re

##############################################################################
# Methods
##############################################################################


def get_install_prefix_from_config_cmake():
    '''
      Parse the config.cmake looking for the CMAKE_INSTALL_PREFIX
    '''
    print("get_underlays_list_from_config_cmaked")
    f = open('config.cmake')
    for line in f:
        # use .*? where ? makes the match non-greedy
        m = re.search('^set\(CMAKE_INSTALL_PREFIX "(.*?)"', line)
        if m:
            return m.group(1)
    return ""


def get_underlays_list_from_config_cmake(base_path=os.getcwd()):
    '''
      Parse the config.cmake looking for the underlays list.
    '''
    f = open(os.path.join(base_path, 'config.cmake'))
    for line in f:
        # use .*? where ? makes the match non-greedy
        m = re.search('^set\(UNDERLAY_ROOTS "(.*?)"', line)
        if m:
            return m.group(1).split(';')
    return []
