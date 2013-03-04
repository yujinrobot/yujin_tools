

import os
import sys
import stat  # file permissions
#import shutil
import argparse
from argparse import RawTextHelpFormatter
import subprocess
import tempfile
# local imports
from .init_build import init_build
import console


def help_string():
    overview = 'This is a convenience script for auto-generating a catkin workspace.\n\n'
    instructions = "It acts on the specified directory (or the current directory if unspecified) and creates:\n\n \
 - ./src : initialised with a catkin CMakeLists.txt and a wstool .rosinstall file.\n \
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
    parser.add_argument('dir', nargs='?', default=os.getcwd(), help='directory to use for the workspace [current working directory]')
    parser.add_argument('-s', '--simple', action='store_true', help='just create a basic single build workspace (usual ros style) [false]')
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
    template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'init_workspace')
    tmpl = read_template(os.path.join(template_dir, filename))
    contents = fill_in_template(tmpl, name, cwd)
    try:
        f = open(os.path.join(cwd, filename), 'w')
        f.write(contents.encode('utf-8'))
    finally:
        os.fchmod(f.fileno(), stat.S_IRWXU)
        f.close()


def init_workspace():
    args = parse_arguments()
    if not which("/opt/ros/groovy/bin/catkin_init_workspace"):
        sys.exit("\nCatkin is not installed: 'sudo apt-get install ros-groovy-catkin'\n")
    if not which("wstool"):
        sys.exit("\nThe workspace tool is not installed: 'sudo apt-get install python-wstool'\n")
    if os.path.isabs(args.dir):
        workspace_dir = args.dir
    else:
        workspace_dir = os.path.join(os.getcwd(), args.dir)
    if not os.path.isdir(workspace_dir):
        os.mkdir(workspace_dir)
    if os.path.isdir(os.path.join(workspace_dir, 'src')):
        sys.exit("This workspace is already initialised")

    console.pretty_println("Creating a workspace in " + workspace_dir, console.bold)
    os.mkdir(os.path.join(workspace_dir, 'src'))
    os.chdir(os.path.join(workspace_dir, 'src'))
    os.system('wstool init . ')
    catkin_init_workspace = create_groovy_script('catkin_init_workspace')
    unused_process = subprocess.call(catkin_init_workspace.name, shell=True)
    os.chdir(workspace_dir)

    if args.simple:
        console.pretty_println("Auto creating a special build directory", console.cyan)
        #init_build()
        # maybe also catkin_make
    else:
        console.pretty_println("Done - add source directories with `wstool` and configure parallel build dirs with 'yujin_init_build'.", console.cyan)

    os.unlink(catkin_init_workspace.name)
