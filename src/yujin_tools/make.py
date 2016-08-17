##############################################################################
# Imports
##############################################################################

#import os
import os.path

import re
import sys
#import stat  # file permissions
import argparse
#from argparse import RawTextHelpFormatter
#import tempfile
import shutil
import multiprocessing
import subprocess
from catkin_pkg.packages import find_packages

##############################################################################
# Local imports
##############################################################################

import console
import config_cache
import common
import settings
from make_doc import make_doc

import catkin_make.terminal_color as terminal_color
from catkin_make.terminal_color import fmt
import catkin_make.builder as builder  # extract_cmake_and_make_arguments, cmake_input_changed

##############################################################################
# Methods
##############################################################################


def _parse_args(args=sys.argv[1:]):
    args, cmake_args, make_args = builder.extract_cmake_and_make_arguments(args)

    parser = argparse.ArgumentParser(description='Creates the catkin workspace layout and invokes cmake and make. Any argument starting with "-D" will be passed to the "cmake" invocation. All other arguments (i.e. target names) are passed to the "make" invocation.')
    parser.add_argument('-j', '--jobs', type=int, metavar='JOBS', default=None, nargs='?', help='Specifies the number of jobs (commands) to run simultaneously. Defaults to the environment variable ROS_PARALLEL_JOBS and falls back to the number of CPU cores.')
    parser.add_argument('--force-cmake', action='store_true', help='Invoke "cmake" even if it has been executed before [false]')
    parser.add_argument('-p', '--pre-clean', action='store_true', help='Clean build temporaries before making [false]')
    parser.add_argument('-c', '--cmake-only', action='store_true', help='Do not compile, just force a re-run of cmake [false]')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', '--install', action='store_true', help='Run install step after making [false]')
    group.add_argument('--track', choices=settings.VALID_TRACKS, dest='default_underlay', action='store', default=None, help='convenience equivalent for the --default-underlay option')
    group.add_argument('--install-rosdeps-track', choices=settings.VALID_TRACKS, action='store', default=None, help='Install all rosdeps for the workspace sources and given track [None]')
    group.add_argument('--install-rosdeps', action='store_true', help='Install all rosdeps for the workspace sources and track set by `yujin_tools_settings --get-default-track` [false]')
    group.add_argument('-t', '--tests', action='store_true', help='Make tests [false]')
    group.add_argument('-r', '--run-tests', action='store_true', help='Run tests (does not build them) [false]')
    parser.add_argument('--strip', action='store_true', help='Strips binaries, only valid with --install')
    parser.add_argument('--no-color', action='store_true', help='Disables colored ouput')
    parser.add_argument('--target', default=None, help='Build against a particular target only')
    parser.add_argument('--pkg', help='Invoke "make" on a specific package only')

    docgroup = parser.add_mutually_exclusive_group()
    docgroup.add_argument('-d', '--doc', action='store_true', help='Generates the documents for packages in the workspace.')
    docgroup.add_argument('--doc-only', action='store_true', help='Generates the documents for packages in the workspace. Does not build source')

    parser.add_argument('--cmake-args', dest='cmake_args', nargs='*', type=str,
        help='Arbitrary arguments which are passes to CMake. It must be passed after other arguments since it collects all following options.')
    parser.add_argument('--make-args', dest='make_args', nargs='*', type=str,
        help='Arbitrary arguments which are passes to make. It must be passed after other arguments since it collects all following options. This is only necessary in combination with --cmake-args since else all unknown arguments are passed to make anyway.')

    options, unknown_args = parser.parse_known_args(args)
    if not options.jobs and not [a for a in args if a == '-j' or a == '--jobs']:
        options.jobs = common.good_number_of_jobs()
    options.cmake_args = cmake_args
    options.make_args = unknown_args + make_args
    return options


def validate_build_space(base_path):
    if not os.path.isfile(os.path.join(base_path, 'config.cmake')):
        raise RuntimeError('Switch to a valid build directory (must contain a config.cmake cmake cache file).')

    # verify that the base path does not contain a CMakeLists.txt
    if os.path.exists(os.path.join(base_path, 'CMakeLists.txt')):
        raise RuntimeError('Switch to a valid build directory (this one is a cmake project, i.e. contains a CMakeLists.txt).')

    # verify that the base path does not contain a package.xml
    if os.path.exists(os.path.join(base_path, 'package.xml')):
        raise RuntimeError('Switch to a valid build directory (this one is a catkin package, i.e. contains a package.xml).')

    # this will have been generated already by yujin_init_build
    source_path = os.path.join(base_path, 'src')
    if os.path.exists(source_path):
        if os.path.islink(source_path):
            absolute_source_path = os.readlink(source_path)
        else:
            absolute_source_path = source_path
        if not os.path.exists(absolute_source_path):
            raise RuntimeError('The specified source space does not exist [%s]' % absolute_source_path)
    else:
        raise RuntimeError('Could not find a valid source path (did you init build correctly?)')


def check_and_update_source_repo_paths(build_source_path):
    '''
      Check that the symbolic links we possible created in the build src directory still
      match the original source directory. If not, update.
    '''
    f = open(os.path.join(build_source_path, '.yujin_init_build'), 'r')
    try:
        rel_path = f.read()
    finally:
        f.close()
    original_source_path = os.path.abspath(os.path.join(build_source_path, rel_path))
    # broken links show up as files
    (unused_root, build_source_subdirectories, files) = os.walk(build_source_path).next()
    for f in files:
        if common.is_broken_symlink(os.path.join(build_source_path, f)):
            build_source_subdirectories.append(f)
    original_source_subdirectories = os.walk(original_source_path).next()[1]
    #print build_source_subdirectories
    #print original_source_subdirectories
    removed = [d for d in build_source_subdirectories if d not in original_source_subdirectories]
    added = [d for d in original_source_subdirectories if d not in build_source_subdirectories]
    for d in removed:
        os.unlink(os.path.join(build_source_path, d))
    for d in added:
        common.create_symlink(os.path.join(original_source_path, d), os.path.join(build_source_path, d), quiet=True)


def insert_yujin_make_signature(yujin_make_root, devel_path):
    '''
      Insert YUJIN_MAKE_ROOT=xxx into devel/setup.bash if the cmake process succeeded. This helps yujin_make
      kickstart itself from anywhere in the future.
    '''
    setup_sh = open(os.path.join(devel_path, 'setup.sh'), 'a+')
    found = False
    for line in setup_sh:
        if re.search('^export YUJIN_MAKE_ROOT', line):
            found = True
            break
    if not found:
        setup_sh.write("export YUJIN_MAKE_ROOT=%s\n" % yujin_make_root)


def install_rosdeps(base_path, source_path, rosdistro, no_color):
    # -r continue even with errors
    cmd = ['rosdep', 'install']  # if you want it to continue installing despite errors, '-r']
    underlays = config_cache.get_underlays_list_from_config_cmake(base_path)
    print("Rosdep Search Paths")
    for underlay in underlays:
        underlay_path = underlay
        underlay_source_path = os.path.abspath(os.path.join(underlay, os.pardir, "src"))
        if os.path.isdir(underlay_source_path):
	    underlay_path = underlay_source_path
        if os.path.isdir(underlay_path):
            cmd += ['--from-paths', underlay_path]
	    print(" - adding underlay '%s'" % underlay_path)
        else:
	    print(" - not adding underlay '%s' [not found]" % underlay_path)
    cmd += ['--from-paths', source_path, '--ignore-src', '--rosdistro', rosdistro, '-y']
    env = os.environ.copy()
    try:
        builder.print_command_banner(cmd, source_path, color=not no_color)
        if no_color:
            builder.run_command(cmd, source_path, env=env)
        else:
            builder.run_command_colorized(cmd, source_path, env=env)
    except subprocess.CalledProcessError:
        return 1  # rosdep will already have provided its own error message, no need to regurgitate
    return 0


def make_main():
    args = _parse_args()
    cmake_args = args.cmake_args

    if args.no_color:
        terminal_color.disable_ANSI_colors()

    (base_path, build_path, devel_path, source_path) = common.get_default_paths()
    doc_path = config_cache.get_doc_prefix_from_config_cmake(base_path)

    validate_build_space(base_path)  # raises a RuntimeError if there is a problem

    # Install rosdeps if requested
    if args.install_rosdeps:
        return install_rosdeps(base_path, source_path, settings.get_default_track(), args.no_color)
    if args.install_rosdeps_track is not None:
        return install_rosdeps(source_path, args.install_rosdeps_track, args.no_color)


    # Clear out previous temporaries if requested
    if args.pre_clean:
        console.pretty_print("Pre-cleaning before building.", console.cyan)
        shutil.rmtree(devel_path, ignore_errors=True)
        shutil.rmtree(build_path, ignore_errors=True)
        shutil.rmtree(doc_path, ignore_errors=True)

    # check for new build
    if not os.path.exists(build_path):
        os.mkdir(build_path)
    #if not os.path.exists(devel_path):
    #    os.mkdir(devel_path)

    # ensure toplevel cmake file exists
    toplevel_cmake = os.path.join(source_path, 'CMakeLists.txt')
    if not os.path.exists(toplevel_cmake):
        return fmt('@{rf}No toplevel cmake file@')

    # did source paths get added to the original location?
    check_and_update_source_repo_paths(source_path)

    packages = find_packages(source_path, exclude_subspaces=True)

    # verify that specified package exists in workspace
    if args.pkg:
        packages_by_name = {p.name: path for path, p in packages.iteritems()}
        if args.pkg not in packages_by_name:
            raise RuntimeError('Package %s not found in the workspace' % args.pkg)

    # check if cmake must be run (either for a changed list of package paths or changed cmake arguments)
    force_cmake, _ = builder.cmake_input_changed(packages, build_path, cmake_args=cmake_args)

    # check if toolchain.cmake, config.cmake exist
    toolchain_cmd = "-DCMAKE_TOOLCHAIN_FILE=%s" % os.path.join(base_path, 'toolchain.cmake') if os.path.isfile(os.path.join(base_path, 'toolchain.cmake')) else None
    config_cmd = "-C%s" % os.path.join(base_path, 'config.cmake') if os.path.isfile(os.path.join(base_path, 'config.cmake')) else None

    # Help find catkin cmake and python
    unused_catkin_toplevel, catkin_python_path, unused_catkin_cmake_path = common.find_catkin(base_path)
    pkg_config_paths = common.generate_pkg_config_path(base_path)
    env = os.environ.copy()
    # PYTHONPATH
    # Don't add to the environment variable - this mucks up catkin's catkin_generated/setup_cached.py
    # environment later (how? I can't remember - something to do with the default underlay).
    # Maybe we can do away with this now catkin can look up install spaces?
    #try:
    #    env['PYTHONPATH'] = env['PYTHONPATH'] + os.pathsep + catkin_python_path
    #except KeyError:
    #    env['PYTHONPATH'] = catkin_python_path
    sys.path.append(catkin_python_path)
    # PKG_CONFIG_PATH
    for path in pkg_config_paths:
        try:
            env['PKG_CONFIG_PATH'] = env['PKG_CONFIG_PATH'] + os.pathsep + path
        except KeyError:
            env['PKG_CONFIG_PATH'] = path

    if args.doc_only:
        console.pretty_println('Generates documents only', console.bold_white)
        make_doc(source_path, doc_path, packages)
        return

    # consider calling cmake
    makefile = os.path.join(build_path, 'Makefile')
    if not os.path.exists(makefile) or args.force_cmake or force_cmake:
        cmd = ['cmake', source_path]
        if toolchain_cmd:
            cmd.append(toolchain_cmd)
        if config_cmd:
            cmd.append(config_cmd)
        cmd += cmake_args

        #new_env = common.generate_underlays_environment(base_path)
        try:
            builder.print_command_banner(cmd, build_path, color=not args.no_color)
            if args.no_color:
                builder.run_command(cmd, build_path, env=env)
            else:
                builder.run_command_colorized(cmd, build_path, env=env)
        except subprocess.CalledProcessError:
            return fmt('@{rf}Invoking @{boldon}"cmake"@{boldoff} failed')
    else:
        cmd = ['make', 'cmake_check_build_system']
        #new_env = common.generate_environment(base_path) # underlays + current workspace
        try:
            builder.print_command_banner(cmd, build_path, color=not args.no_color)
            if args.no_color:
                builder.run_command(cmd, build_path, env=env)
            else:
                builder.run_command_colorized(cmd, build_path, env=env)
        except subprocess.CalledProcessError:
            return fmt('@{rf}Invoking @{boldon}"make cmake_check_build_system"@{boldoff} failed')

    insert_yujin_make_signature(base_path, devel_path)

    # invoke make
    if not args.cmake_only:
        if args.target:
            cmd = ['make', args.target]
        elif args.install:
            cmd = ['make', 'install/strip'] if args.strip else ['make', 'install']
        elif args.tests:
            cmd = ['make', 'tests']
        elif args.run_tests:
            cmd = ['make', 'test']
        else:
            cmd = ['make']
        jobs = args.jobs
        if args.jobs == '':
            cmd.append('-j')
        else:
            jobs = args.jobs
            if not jobs:
                if 'ROS_PARALLEL_JOBS' in os.environ:
                    ros_parallel_jobs = os.environ['ROS_PARALLEL_JOBS']
                    cmd += [arg for arg in ros_parallel_jobs.split(' ') if arg]
                else:
                    jobs = multiprocessing.cpu_count()
            if jobs:
                cmd.append('-j%d' % jobs)
                cmd.append('-l%d' % jobs)
        cmd += args.make_args
        try:
            make_path = build_path
            if args.pkg:
                make_path = os.path.join(make_path, packages_by_name[args.pkg])
            builder.print_command_banner(cmd, make_path, color=not args.no_color)
            builder.run_command(cmd, make_path, env=env)
        except subprocess.CalledProcessError:
            return fmt('@{rf}Invoking @{boldon}"make"@{boldoff} failed')

    if args.doc:
        make_doc(source_path, doc_path, packages)
