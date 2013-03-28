##############################################################################
# Imports
##############################################################################

import os.path

import sys
#import stat  # file permissions
import argparse
from argparse import RawTextHelpFormatter
#import shutil

##############################################################################
# Local imports
##############################################################################

import console
#import common

##############################################################################
# Constants
##############################################################################

DEFAULT_TRACK = "groovy"
VALID_TRACKS = ["groovy", "hydro"]

##############################################################################
# Methods
##############################################################################


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

##############################################################################
# Utility Settings Script Functionality
##############################################################################


def help_string():
    overview = '\nThis is a convenience script for configuring yujin tools settings.\n\n'
    instructions = " \
 - 'yujin_tools_settings --get-default-track' : return the currently configured default track.\n \
 - 'yujin_tools_settings --set-default-track hydro' : save this track as the default track in yujin_tools_home.\n \
 "
    return overview + instructions


def parse_arguments():
    parser = argparse.ArgumentParser(description=help_string(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--get-default-track', action='store_true', help='print the default track that is being followed to screen')
    parser.add_argument('--set-default-track', action='store', default=None, help='set a new default track to work from %s' % VALID_TRACKS)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    if args.get_default_track:
        #console.pretty_print("\nDefault Track: ", console.cyan)
        #console.pretty_println("%s\n" % get_default_track(), console.yellow)
        print get_default_track()
        sys.exit(0)
    if args.set_default_track:
        console.pretty_print("\nNew Default Track: ", console.cyan)
        console.pretty_println("%s\n" % set_default_track(args.set_default_track), console.yellow)
        sys.exit(0)
    print("%s" % help_string())
