

import os
import os.path

import sys
import stat  # file permissions
import argparse
from argparse import RawTextHelpFormatter
import subprocess
import tempfile
import console


def help_string():
    overview = 'This is a convenience script for auto-generating a catkin parallel build directory.\n\n'
    instructions = "Can be used standalone, or with optional build directory and source directory targets:\n\n \
 - 'yujin_init_build' prepares a build directory in ./debug linked to ./src \n \
 - 'yujin_init_build --release release' prepares a release directory in ./release linked to ./src \n \
 - 'yujin_init_build debug ~/ecl/src' prepares a build directory in ./debug linked to ~/ecl/src \n \
"
    return overview + instructions


def create_groovy_script(script_name):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write("#!/bin/bash\n")
    f.write("source /opt/ros/groovy/setup.bash\n")
    f.write(script_name + "\n")
    os.chmod(f.name, stat.S_IRWXU)
    f.close()
    return f


def parse_arguments():
    parser = argparse.ArgumentParser(description=help_string(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('dir', nargs='?', default="debug", help='directory to use for the parallel development space [debug]')
    parser.add_argument('sources', nargs='?', default="src", help='directory where the sources reside [src]')
    parser.add_argument('-r', '--release', action='store_true', help='build in Release mode instead of RelWithDebugSymbols [false]')
    parser.add_argument('-i', '--install', action='store', default='/not_set_directory', help='installation location [workspace/install]')
    parser.add_argument('-u', '--underlay', action='store', default='/opt/ros/groovy', help='semi-colon list of catkin workspaces to utilise [/opt/ros/groovy]')
    args = parser.parse_args()
    return args


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


def read_template(tmplf):
    f = open(tmplf, 'r')
    try:
        t = f.read()
    finally:
        f.close()
    return t


def fill_in_template(template, name, cwd):
    return template % locals()


def instantiate_template(filename, name, cwd):
    template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'init_build')
    tmpl = read_template(os.path.join(template_dir, filename))
    contents = fill_in_template(tmpl, name, cwd)
    try:
        f = open(os.path.join(cwd, filename), 'w')
        f.write(contents.encode('utf-8'))
    finally:
        os.fchmod(f.fileno(), stat.S_IRWXU)
        f.close()


def fill_in_makefile(template, cwd, source_directory, underlays, install_prefix, build_type):
    return template % locals()


def instantiate_makefile(filename, cwd, source_directory, underlays, install_prefix, build_type):
    template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'init_build')
    tmpl = read_template(os.path.join(template_dir, filename))
    contents = fill_in_makefile(tmpl, cwd, source_directory, underlays, install_prefix, build_type)
    try:
        f = open(os.path.join(cwd, filename), 'w')
        f.write(contents.encode('utf-8'))
    finally:
        #os.fchmod(f.fileno(), stat.S_IRWU)
        f.close()


def init_build():
    source_directory = None
    args = parse_arguments()
    ##########################
    # Build directory
    ##########################
    if os.path.isabs(args.dir):
        build_dir = args.dir
    else:
        build_dir = os.path.join(os.getcwd(), args.dir)
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    else:
        console.logerror("This build directory is already initialised")
        sys.exit(1)
    ##########################
    # Source directory
    ##########################
    if os.path.isabs(args.sources):
        source_directory = args.sources
    else:
        source_directory = os.path.join(os.getcwd(), args.sources)
    if not os.path.isdir(source_directory):
        console.logerror("Specified source folder does not exist [" + source_directory + "]")
        sys.exit(1)
    if not os.path.isfile(os.path.join(source_directory, ".rosinstall")):
        console.logerror("Could not find a valid source folder (must contain a .rosinstall file therein)'")
        sys.exit(1)
    ##########################
    # Other Args
    ##########################
    if args.install == "/not_set_directory":
        install_prefix = os.path.join(build_dir, "install")
    else:
        install_prefix = args.install
    if args.release:
        build_type = "Release"
    else:
        build_type = "DebugWithRelSymbols"

    console.pretty_println("*********** Parallel Development Workspace Details ***********", console.bold)
    console.pretty_print("Build directory : ", console.cyan)
    console.pretty_println(build_dir, console.yellow)
    console.pretty_print("Source directory: ", console.cyan)
    console.pretty_println(source_directory, console.yellow)
    console.pretty_print("Install prefix  : ", console.cyan)
    console.pretty_println(install_prefix, console.yellow)
    console.pretty_print("Build Type      : ", console.cyan)
    console.pretty_println(build_type, console.yellow)
    console.pretty_print("Underlays        : ", console.cyan)
    console.pretty_println(args.underlay, console.yellow)
    console.pretty_println("**************************************************************", console.bold)

    os.chdir(build_dir)

    name = os.path.basename(build_dir)
    instantiate_template('.bashrc', name, build_dir)
    instantiate_template('konsole', name, build_dir)
    instantiate_template('gnome-terminal', name, build_dir)
    instantiate_template('eclipse', name, build_dir)
    instantiate_makefile('Makefile', os.path.relpath(build_dir, os.getcwd()), os.path.relpath(source_directory, build_dir), args.underlay, install_prefix, build_type)
