'''
Created on Mar 27, 2013

@author: snorri
'''

import os
import sys
import tempfile
# Local imports
import console

DEFAULT_TRACK = "groovy"
VALID_TRACKS = ["groovy", "hydro"]


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


def yujin_tools_home():
    """
    Get directory location of '.yujin_tools' directory (aka Yujin Tools home).

    @param env: override os.environ dictionary
    @type  env: dict
    @return: path to use use for log file directory
    @rtype: str
    """
    home_dir = os.path.join(os.path.expanduser('~'), '.yujin_tools')
    if not os.path.exists(home_dir):
        os.makedirs(home_dir)
    return home_dir


def get_default_track():
    filename = os.path.join(yujin_tools_home(), "track")
    try:
        f = open(filename, 'r')
    except IOError:
        set_default_track()
        return DEFAULT_TRACK
    track = f.read()
    f.close()
    return track


def set_default_track(track=DEFAULT_TRACK):
    if track not in VALID_TRACKS:
        console.logerror("The track '%s' is not a valid track. Choose from %s\n" % (track, VALID_TRACKS))
        sys.exit(1)
    filename = os.path.join(yujin_tools_home(), "track")
    f = open(filename, 'w+')
    try:
        f.write(track.encode('utf-8'))
    finally:
        f.close()
    return track


def create_environment_script(script_name):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write("#!/bin/bash\n")
    f.write("source /opt/ros/groovy/setup.bash\n")
    f.write(script_name + "\n")
    os.chmod(f.name, stat.S_IRWXU)
    f.close()
    return f
