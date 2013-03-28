##############################################################################
# Imports
##############################################################################

import os
import sys
from distutils.sysconfig import get_python_lib

##############################################################################
# Local imports
##############################################################################

##############################################################################
# Methods
##############################################################################


def get_global_python_destination():
    '''
      Should introduce variance in here for the different platforms.
      (windows is always site-packages - see the cmake/python.cmake)
    '''
    # get_python_lib() returns something like /usr/python2.7/dist-packages
    dest = os.path.join('lib', 'python%u.%u' % (sys.version_info[0], sys.version_info[1]), os.path.basename(get_python_lib()))
    # this doesn't work
    #if '--install-layout=deb' not in sys.argv[1:]:
    #    dest += 'site-packages'
    #else:
    #    dest += 'dist-packages'
    return dest
