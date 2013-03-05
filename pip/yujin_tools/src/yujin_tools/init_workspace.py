

import os
import sys
import stat  # file permissions
#import shutil
import argparse
from argparse import RawTextHelpFormatter
import subprocess
import tempfile
import urlparse
import yaml
import urllib2
# local imports
from .init_build import init_configured_build
import console


def help_string():
    overview = 'This is a convenience script for auto-generating a catkin workspace.\n\n'
    instructions = " \
 - 'yujin_init_workspace ecl' : create an empty workspace in ./ecl.\n \
 - 'yujin_init_workspace ~/ecl' : create an empty workspace in ~/ecl.\n \
 - 'yujin_init_workspace ecl ecl.rosinstall' : populate a workspace from rosinstall file.\n \
 - 'yujin_init_workspace ecl ecl' : populate a workspace from our rosinstall database.\n \
 - 'yujin_init_workspace ecl https://raw.github.com/stonier/ecl_core/groovy-devel/ecl.rosinstall' : populate from uri.\n\n \
 If you wish to add to the rosinstall database, edit and pull request at\n\n \
     https://github.com/yujinrobot/yujin_tools/blob/master/pip/yujin_tools/rosinstalls/groovy.yaml\n \
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
    parser.add_argument('uri', nargs='?', default=None, help='uri for a rosinstall file [None]')
    parser.add_argument('-s', '--simple', action='store_true', help='just create a basic single build workspace (usual ros style) [false]')
    parser.add_argument('--list-rosinstalls', action='store_true', help='list all currently available rosinstalls [false]')
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


def list_rosinstalls():
    response = urllib2.urlopen('https://raw.github.com/yujinrobot/yujin_tools/master/pip/yujin_tools/rosinstalls/groovy.yaml')
    rosinstalls = yaml.load(response.read())
    for r in rosinstalls.keys():
        console.pretty_print(" " + r + ": ", console.cyan)
        console.pretty_println(rosinstalls[r], console.yellow)


def init_workspace():
    args = parse_arguments()
    if args.list_rosinstalls:
        list_rosinstalls()
        sys.exit(0)
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
    if args.uri:
        uri = args.uri  # assume its an absolute path or http uri
        if not os.path.isabs(args.uri):
            if os.path.isfile(os.path.join(os.getcwd(), args.uri)):
                uri = os.path.join(os.getcwd(), args.uri)
            else:
                if urlparse.urlparse(args.uri).scheme == "":  # not a http element, let's look up our databas
                    response = urllib2.urlopen('https://raw.github.com/yujinrobot/yujin_tools/master/pip/yujin_tools/rosinstalls/groovy.yaml')
                    rosinstalls = yaml.load(response.read())
                    if args.uri in rosinstalls:
                        uri = rosinstalls[args.uri]
                        print("Retrived uri from the yujin_tools rosinstall database: %s" % uri)
                    else:
                        console.logerror("Uri not an absolute path, local file, http or in our rosinstall database.")
                        sys.exit(1)
    else:
        uri = ""
    console.pretty_println("Creating a workspace in " + workspace_dir, console.bold)
    os.mkdir(os.path.join(workspace_dir, 'src'))
    os.chdir(os.path.join(workspace_dir, 'src'))
    if uri:
        os.system('wstool init . ' + uri)
        # os.system('wstool update') Not needed if adding the uri to wstool init
    else:
        os.system('wstool init . ')
    catkin_init_workspace = create_groovy_script('catkin_init_workspace')
    unused_process = subprocess.call(catkin_init_workspace.name, shell=True)
    os.chdir(workspace_dir)

    if args.simple:
        console.pretty_println("Auto creating a special build directory", console.cyan)
        init_configured_build()
    else:
        console.pretty_println("Done - add source directories with `wstool` and configure parallel build dirs with 'yujin_init_build'.", console.cyan)

    os.unlink(catkin_init_workspace.name)
