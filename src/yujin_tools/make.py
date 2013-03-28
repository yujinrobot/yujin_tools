##############################################################################
# Imports
##############################################################################

#import os
import os.path

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
import common

import catkin_make.terminal_color as terminal_color
from catkin_make.terminal_color import fmt
import catkin_make.builder as builder  # extract_cmake_and_make_arguments, cmake_input_changed

##############################################################################
# Methods
##############################################################################


def _parse_args(args=sys.argv[1:]):
    args, cmake_args, make_args = builder.extract_cmake_and_make_arguments(args)

    parser = argparse.ArgumentParser(description='Creates the catkin workspace layout and invokes cmake and make. Any argument starting with "-D" will be passed to the "cmake" invocation. All other arguments (i.e. target names) are passed to the "make" invocation.')
    parser.add_argument('--source', help='The path to the source space (default "src")')
    parser.add_argument('-j', '--jobs', type=int, metavar='JOBS', nargs='?', help='Specifies the number of jobs (commands) to run simultaneously. Defaults to the environment variable ROS_PARALLEL_JOBS and falls back to the number of CPU cores.')
    parser.add_argument('--force-cmake', action='store_true', help='Invoke "cmake" even if it has been executed before [false]')
    parser.add_argument('-p', '--pre-clean', action='store_true', help='Clean build temporaries before making [false]')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', '--install', action='store_true', help='Run install step after making [false]')
    group.add_argument('-t', '--tests', action='store_true', help='Make tests [false]')
    group.add_argument('-r', '--run_tests', action='store_true', help='Make and run tests [false]')
    parser.add_argument('--no-color', action='store_true', help='Disables colored ouput')
    parser.add_argument('--pkg', help='Invoke "make" on a specific package only')
    parser.add_argument('--cmake-args', dest='cmake_args', nargs='*', type=str,
        help='Arbitrary arguments which are passes to CMake. It must be passed after other arguments since it collects all following options.')
    parser.add_argument('--make-args', dest='make_args', nargs='*', type=str,
        help='Arbitrary arguments which are passes to make. It must be passed after other arguments since it collects all following options. This is only necessary in combination with --cmake-args since else all unknown arguments are passed to make anyway.')

    namespace, unknown_args = parser.parse_known_args(args)
    # support -j/--jobs without an argument which argparse can not distinguish
    if not namespace.jobs and [a for a in args if a == '-j' or a == '--jobs']:
        namespace.jobs = ''
    namespace.cmake_args = cmake_args
    namespace.make_args = unknown_args + make_args
    return namespace


def make_main():
    args = _parse_args()
    cmake_args = args.cmake_args

    # disable colors if asked
    if args.no_color:
        terminal_color.disable_ANSI_colors()

    # Default paths
    base_path = os.path.abspath('.')
    build_path = os.path.join(base_path, 'build')
    devel_path = os.path.join(base_path, 'devel')

    # verify that the base path does not contain a CMakeLists.txt, except if base path equals source path
    if (args.source is None or os.path.realpath(base_path) != os.path.realpath(args.source)) and os.path.exists(os.path.join(base_path, 'CMakeLists.txt')):
        return fmt('@{rf}The specified base path @{boldon}"%s"@{boldoff} contains a CMakeLists.txt but "catkin_make" must be invoked in the root of workspace' % base_path)

    # verify that the base path does not contain a package.xml
    if os.path.exists(os.path.join(base_path, 'package.xml')):
        return fmt('@{rf}The specified base path @{boldon}"%s"@{boldoff} contains a package but "catkin_make" must be invoked in the root of workspace' % base_path)

    # this will have been generated already by yujin_init_build
    source_path = os.path.join(base_path, 'src')
    if os.path.exists(source_path):
        if os.path.islink(source_path):
            absolute_source_path = os.readlink(source_path)
        else:
            absolute_source_path = source_path
        if not os.path.exists(absolute_source_path):
            return fmt('@{rf}The specified source space @{boldon}"%s"@{boldoff} does not exist' % absolute_source_path)
    else:
        return fmt('@{rf}Could not find a valid source path (did you init build correctly?)')

    # Clear out previous temporaries if requested
    if args.pre_clean:
        console.pretty_print("Pre-cleaning before building.", console.cyan)
        shutil.rmtree(devel_path, ignore_errors=True)
        shutil.rmtree(build_path, ignore_errors=True)

    # check for new build
    if not os.path.exists(build_path):
        os.mkdir(build_path)

    # ensure toplevel cmake file exists
    toplevel_cmake = os.path.join(source_path, 'CMakeLists.txt')
    if not os.path.exists(toplevel_cmake):
        return fmt('@{rf}No toplevel cmake file@')

    packages = find_packages(source_path, exclude_subspaces=True)

    # verify that specified package exists in workspace
    if args.pkg:
        packages_by_name = {p.name: path for path, p in packages.iteritems()}
        if args.pkg not in packages_by_name:
            return fmt('@{rf}Package @{boldon}"%s"@{boldoff} not found in the workspace' % args.pkg)

    # check if cmake must be run (either for a changed list of package paths or changed cmake arguments)
    force_cmake, _ = builder.cmake_input_changed(packages, build_path, cmake_args=cmake_args)

    # check if toolchain.cmake, config.cmake exist
    toolchain_cmd = "-DCMAKE_TOOLCHAIN_FILE=%s" % os.path.join(base_path, 'toolchain.cmake') if os.path.isfile(os.path.join(base_path, 'toolchain.cmake')) else None
    config_cmd = "-C%s" % os.path.join(base_path, 'config.cmake') if os.path.isfile(os.path.join(base_path, 'config.cmake')) else None

    # consider calling cmake
    makefile = os.path.join(build_path, 'Makefile')
    if not os.path.exists(makefile) or args.force_cmake or force_cmake:
        cmd = ['cmake', source_path]
        if toolchain_cmd:
            cmd.append(toolchain_cmd)
        if config_cmd:
            cmd.append(config_cmd)
        cmd += cmake_args
        print cmd
        try:
            builder.print_command_banner(cmd, build_path, color=not args.no_color)
            if args.no_color:
                builder.run_command(cmd, build_path)
            else:
                builder.run_command_colorized(cmd, build_path)
        except subprocess.CalledProcessError:
            return fmt('@{rf}Invoking @{boldon}"cmake"@{boldoff} failed')
    else:
        cmd = ['make', 'cmake_check_build_system']
        try:
            builder.print_command_banner(cmd, build_path, color=not args.no_color)
            if args.no_color:
                builder.run_command(cmd, build_path)
            else:
                builder.run_command_colorized(cmd, build_path)
        except subprocess.CalledProcessError:
            return fmt('@{rf}Invoking @{boldon}"make cmake_check_build_system"@{boldoff} failed')

    # invoke make
    if args.install:
        cmd = ['make', 'install']
    elif args.tests:
        cmd = ['make', 'tests']
    elif args.run_tests:
        cmd = ['make', 'run_tests']
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
        builder.run_command(cmd, make_path)
    except subprocess.CalledProcessError:
        return fmt('@{rf}Invoking @{boldon}"make"@{boldoff} failed')
