##############################################################################
# Imports
##############################################################################

import os
import sys
import multiprocessing

##############################################################################
# Local imports
##############################################################################

import console
import python_setup
import config_cache

##############################################################################
# Methods
##############################################################################


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


def is_same_dir(dir_a, dir_b):
    rel_path = os.path.relpath(os.path.abspath(dir_a), os.path.abspath(dir_b))
    if rel_path == ".":
        return True
    else:
        return False


#def modified_environment(catkin_python_path, env=None):
#    '''
#      Prepends the path to the PYTHONPATH environment variable.
#      Could use some checking to make sure it is a single path, not a
#      pathsep list.
#    '''
#    if not env:
#        env = os.environ.copy()
#    try:
#        env['PYTHONPATH'] = env['PYTHONPATH'] + os.pathsep + catkin_python_path
#    except KeyError:
#        env['PYTHONPATH'] = catkin_python_path

def good_number_of_jobs():
    if 'ROS_PARALLEL_JOBS' in os.environ:
        jobs = os.environ['ROS_PARALLEL_JOBS']
    else:
        try:
            jobs = multiprocessing.cpu_count()
        except NotImplementedError:
            jobs = 1
    return jobs


def override_filename():
    return os.path.join(os.path.dirname(__file__), 'cmake', 'overrides.cmake')


def parent_directory(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def create_symlink(src, dst, quiet=False):
    """
    Creates a symlink at dst to src.
    """
    if not os.path.exists(src):
        raise RuntimeError("'%s' is not a valid path" % src)
    try:
        os.symlink(src, dst)
        if not quiet:
            console.pretty_print('Creating symlink', console.white)
            console.pretty_print(' "%s" ' % dst, console.bold)
            console.pretty_print("->", console.white)
            console.pretty_println(' "%s." ' % src, console.bold)
    except Exception as ex_symlink:
        raise RuntimeError("Could not symlink '%s' to %s [%s]." % (src, dst, str(ex_symlink)))


def is_broken_symlink(link_path):
    '''
      Checks to see if the provided link_path is firstly, a link, and secondly if
      that link is broken.
    '''
    if os.path.islink(link_path):
        target_path = os.readlink(link_path)
        # Resolve relative symlinks
        if not os.path.isabs(target_path):
            target_path = os.path.join(os.path.dirname(link_path), target_path)
        if not os.path.exists(target_path):
            return True
    return False


def find_catkin(base_path, underlays_list=None):
    '''
      Search the underlays looking for catkin's toplevel.cmake and python module.
    '''
    if underlays_list is None:
        underlays_list = config_cache.get_underlays_list_from_config_cmake(base_path)
    catkin_toplevel = None
    catkin_python_path = None
    catkin_cmake_path = None
    for underlay in underlays_list:
        if os.path.isfile(os.path.join(underlay, 'share', 'catkin', 'cmake', 'toplevel.cmake')):
            catkin_cmake_path = os.path.join(underlay, 'share', 'catkin', 'cmake')
            catkin_toplevel = os.path.join(underlay, 'share', 'catkin', 'cmake', 'toplevel.cmake')
            if os.path.isfile(os.path.join(underlay, python_setup.get_global_python_destination(), 'catkin', 'builder.py')):
                catkin_python_path = os.path.join(underlay, python_setup.get_global_python_destination())
            break
    return catkin_toplevel, catkin_python_path, catkin_cmake_path


def get_default_paths(isolated=False):
    suffix = "_isolated" if isolated else ""
    base_path = os.environ.get("YUJIN_MAKE_ROOT") or os.getcwd()  # Fallback if os.environ.get returns None
    build_path = os.path.join(base_path, 'build' + suffix)
    devel_path = os.path.join(base_path, 'devel' + suffix)
    source_path = os.path.join(base_path, 'src')
    return (base_path, build_path, devel_path, source_path)
