'''
Created on Mar 27, 2013

@author: snorri
'''

import os
import sys
import re
#import tempfile
import shutil
# Local imports
import console
import python_setup


def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, unused_fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def override_filename():
    return os.path.join(os.path.dirname(__file__), 'cmake', 'overrides.cmake')


def parent_directory(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def get_underlays_list_from_config_cmake():
    '''
      Parse the config.cmake looking for the underlays list.
    '''
    f = open('config.cmake')
    for line in f:
        m = re.search('^set\(UNDERLAY_ROOTS "(.*)"', line)
        if m:
            return m.group(1).split(';')
    return []


def create_symlink(src, dst):
    """
    Creates a symlink at dst to src.
    """
    if not os.path.exists(src):
        console.logerror("'%s' is not a valid path" % src)
        sys.exit(1)
    try:
        os.symlink(src, dst)
        console.pretty_print('Creating symlink', console.white)
        console.pretty_print(' "%s" ' % dst, console.bold)
        console.pretty_print("->", console.white)
        console.pretty_println(' "%s." ' % src, console.bold)
    except Exception as ex_symlink:
        console.logerror("Could not symlink '%s' to %s [%s]." % (src, dst, str(ex_symlink)))
        raise RuntimeError()


def find_catkin(underlays_list):
    '''
      Search the underlays looking for catkin's toplevel.cmake and python module.
    '''
    catkin_toplevel = None
    catkin_python_path = None
    for underlay in underlays_list:
        if os.path.isfile(os.path.join(underlay, 'share', 'catkin', 'cmake', 'toplevel.cmake')):
            catkin_toplevel = os.path.join(underlay, 'share', 'catkin', 'cmake', 'toplevel.cmake')
            if os.path.isfile(os.path.join(underlay, python_setup.get_global_python_destination(), 'catkin', 'builder.py')):
                catkin_python_path = os.path.join(underlay, python_setup.get_global_python_destination())
            break
    return catkin_toplevel, catkin_python_path
