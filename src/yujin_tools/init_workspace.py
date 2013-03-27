##############################################################################
# Imports
##############################################################################

import os
import sys
import argparse
from argparse import RawTextHelpFormatter
import urlparse
import yaml
import urllib2

##############################################################################
# Local imports
##############################################################################

from .init_build import init_configured_build
import console
import common

##############################################################################
# Import checks
##############################################################################

try:
    import wstool.wstool_cli
except ImportError:
    sys.exit("\nThe workspace tool is not installed: 'sudo apt-get install python-wstool'\n")

##############################################################################
# Methods
##############################################################################


def help_string():
    overview = 'This is a convenience script for auto-generating a catkin workspace.\n\n'
    instructions = " \
 - 'yujin_init_workspace ecl' : create an empty workspace in ./ecl.\n \
 - 'yujin_init_workspace ~/ecl' : create an empty workspace in ~/ecl.\n \
 - 'yujin_init_workspace ecl ecl.rosinstall' : populate a workspace from rosinstall file.\n \
 - 'yujin_init_workspace ecl ecl' : populate a workspace from our rosinstall database from the deafult track.\n \
 - 'yujin_init_workspace --get-default-track' : shows the currently set default track.\n \
 - 'yujin_init_workspace --set-default-track=groovy' : sets the currently set default track.\n \
 - 'yujin_init_workspace --track=hydro ecl ecl' : populate a workspace from our rosinstall database for hydro.\n \
 - 'yujin_init_workspace ecl https://raw.github.com/stonier/ecl_core/groovy-devel/ecl.rosinstall' : populate from uri.\n\n \
 If you wish to add to the rosinstall database, edit and pull request at\n\n \
     https://github.com/yujinrobot/yujin_tools/blob/master/pip/yujin_tools/rosinstalls/groovy.yaml\n \
 "
    return overview + instructions


def parse_arguments():
    parser = argparse.ArgumentParser(description=help_string(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('dir', nargs='?', default=os.getcwd(), help='directory to use for the workspace [current working directory]')
    parser.add_argument('uri', nargs='?', default=None, help='uri for a rosinstall file [None]')
    parser.add_argument('-s', '--simple', action='store_true', help='just create a basic single build workspace (usual ros style) [false]')
    parser.add_argument('--list-rosinstalls', action='store_true', help='list all currently available rosinstalls [false]')
    parser.add_argument('-t', '--track', action='store', default=None, help='retrieve rosinstalls relevant to this track [groovy|hydro][groovy]')
    parser.add_argument('--get-default-track', action='store_true', help='print the default track that is being followed to screen')
    parser.add_argument('--set-default-track', action='store', default=None, help='set a new default track to work from %s' % common.VALID_TRACKS)
    args = parser.parse_args()
    return args


def populate_worskpace(base_path, rosinstall_file_uri):
    '''
      @param base_path : location of the wstool workspace
      @param rosinstall_file_uri : the uri for the rosinstall file
    '''
    wstool_arguments = ['wstool',
                        'init',
                        base_path,
                        rosinstall_file_uri,
                        ]
    wstool.wstool_cli.wstool_main(wstool_arguments)

def list_rosinstalls(track):
    response = urllib2.urlopen('https://raw.github.com/yujinrobot/yujin_tools/master/rosinstalls/%s.yaml' % track)
    rosinstalls = yaml.load(response.read())
    for r in rosinstalls.keys():
        console.pretty_print(" " + r + ": ", console.cyan)
        console.pretty_println(rosinstalls[r], console.yellow)


def init_workspace():
    args = parse_arguments()
    if args.get_default_track:
        console.pretty_print("\nDefault Track: ", console.cyan)
        console.pretty_println("%s\n" % common.get_default_track(), console.yellow)
        sys.exit(0)
    if args.set_default_track:
        console.pretty_print("\nNew Default Track: ", console.cyan)
        console.pretty_println("%s\n" % common.set_default_track(args.set_default_track), console.yellow)
        sys.exit(0)
    if not args.track:
        args.track = common.get_default_track()
    if args.list_rosinstalls:
        list_rosinstalls(args.track)
        sys.exit(0)
#    if not which("/opt/ros/" + args.track + "/bin/catkin_init_workspace"):
#        sys.exit("\nCatkin is not installed: 'sudo apt-get install ros-%s-catkin'\n" % args.track)
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
                    response = urllib2.urlopen('https://raw.github.com/yujinrobot/yujin_tools/master/rosinstalls/%s.yaml' % args.track)
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
    populate_worskpace(os.path.join(workspace_dir, 'src'), uri)
    console.pretty_println("Done - add source directories with `wstool` and configure parallel build dirs with 'yujin_init_build'.", console.cyan)
