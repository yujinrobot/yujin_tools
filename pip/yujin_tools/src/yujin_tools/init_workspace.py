

import os
import sys
import stat # file permissions
import shutil
import argparse
from argparse import RawTextHelpFormatter
import subprocess
import tempfile

def help_string():
    overview = 'This is a convenience script for auto-generating a catkin workspace, particularly for the lads who are cross-compiling.\n\n'
    instructions = "It acts on the current directory and creates:\n\n \
 - ./src : initialised with a catkin CMakeLists.txt and a wstool .rosinstall file.\n \
 - ./build : for native build temporaries\n \
 - ./devel : for a native runtime area.\n \
 - ./cross : for cross compiled build temporaries. \n \
 - ./fakeroot : for cross compiled installs. \n \
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
    #parser.add_argument('-d', '--debug', action='store_true', help='print debugging information')
    args = parser.parse_args()
    return args

def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
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
    f = open(tmplf,'r')
    try:
        t = f.read()
    finally:
        f.close()
    return t

def fill_in_template(template, name, cwd):
    return template%locals()

def instantiate_template(filename, name, cwd):
    template_dir = os.path.join(os.path.dirname(__file__),'templates','init_workspace')
    tmpl = read_template(os.path.join(template_dir,filename))
    contents = fill_in_template(tmpl, name, cwd)
    try:
        f = open ( os.path.join(cwd, filename), 'w')
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
    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd,'src')):
        sys.exit("This workspace is already initialised")
    os.mkdir(os.path.join(cwd,'src'))
    os.mkdir(os.path.join(cwd,'cross')) 
    os.mkdir(os.path.join(cwd,'native')) 
    os.chdir(os.path.join(cwd,'src'))
    os.system('wstool init')
    catkin_init_workspace = create_groovy_script('catkin_init_workspace')
    process = subprocess.call(catkin_init_workspace.name, shell=True)
    os.chdir(cwd)

    name = os.path.basename(cwd)
    template_dir = os.path.join(os.path.dirname(__file__),'templates','init_workspace')
    shutil.copy(os.path.join(template_dir,'Makefile'), os.path.join(cwd,'native'))
    shutil.copy(os.path.join(template_dir,'Makefile'), os.path.join(cwd,'cross'))
    shutil.copy(os.path.join(template_dir,'setup.bash'), cwd)
    os.chmod(os.path.join(cwd, 'setup.bash'), stat.S_IRWXU)
    instantiate_template('.bashrc',name, cwd)
    instantiate_template('konsole',name, cwd)
    instantiate_template('gnome-terminal',name, cwd)
    instantiate_template('eclipse',name, cwd)

    os.unlink(catkin_init_workspace.name)



