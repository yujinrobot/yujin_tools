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

import console
import settings

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
 Note that the track options only apply if you are using a rosinstall database (use yujin_tools_settings to configure)\n\n \
 "
    return overview + instructions


def parse_arguments():
    parser = argparse.ArgumentParser(description=help_string(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('dir', nargs='?', default=os.getcwd(), help='directory to use for the workspace [current working directory]')
    parser.add_argument('-s', '--simple', action='store_true', help='just create a basic single build workspace (usual ros style) [false]')
    parser.add_argument('--list-rosinstalls', action='store_true', help='list all currently available rosinstalls [false]')
    parser.add_argument('--track', action='store', default=None, help='retrieve rosinstalls relevant to this track [groovy|hydro][groovy]')
    parser.add_argument('-j', '--jobs', action='store', default=1, help='how many parallel threads to use for installing[1]')
    parser.add_argument('uri', nargs=argparse.REMAINDER, default=None, help='uri for a rosinstall file [None]')
    args = parser.parse_args()
    return args


def populate_worskpace(base_path, uri_list, parallel_jobs):
    '''
      @param base_path : location of the wstool workspace
      @param uri : the uri for the rosinstall file
    '''
    wstool_arguments = ['wstool',
                        'init',
                        '-j %s' % str(parallel_jobs),
                        base_path,
                        ]
    #print("%s" % uri_list)
    for uri in uri_list:
        wstool_arguments.append(uri)
    wstool.wstool_cli.wstool_main(wstool_arguments)


def list_rosinstalls(track):
    response = urllib2.urlopen('%s/%s.yaml' % (settings.get_rosinstall_database_uri(), track))
    rosinstalls = yaml.load(response.read())
    for r in rosinstalls.keys():
        console.pretty_print(" " + r + ": ", console.cyan)
        console.pretty_println(rosinstalls[r], console.yellow)


def init_workspace():
    args = parse_arguments()
    if not args.track:
        args.track = settings.get_default_track()
    if args.list_rosinstalls:
        list_rosinstalls(args.track)
        sys.exit(0)
    if os.path.isabs(args.dir):
        workspace_dir = args.dir
    else:
        workspace_dir = os.path.join(os.getcwd(), args.dir)
    if not os.path.isdir(workspace_dir):
        os.mkdir(workspace_dir)
    if os.path.isdir(os.path.join(workspace_dir, 'src')):
        raise RuntimeError("This workspace is already initialised")
    lookup_name = None
    lookup_database = None
    lookup_track = None
    uri_list = []
    for uri in args.uri:
        if os.path.isabs(uri):
            uri_list.append(uri)
        else:
            if os.path.isfile(os.path.join(os.getcwd(), uri)):
                uri_list.append(os.path.join(os.getcwd(), uri))
            else:
                if urlparse.urlparse(uri).scheme == "":  # not a http element, let's look up our databas
                    lookup_name = uri
                    lookup_track = args.track
                    lookup_database = settings.get_rosinstall_database_uri()
                    response = urllib2.urlopen('%s/%s.yaml' % (lookup_database, args.track))
                    rosinstalls = yaml.load(response.read())
                    if uri in rosinstalls:
                        uri_list.append(rosinstalls[uri])
                    else:
                        raise RuntimeError("Uri not an absolute path, local file, http or in our rosinstall database.")
    populate_worskpace(os.path.join(workspace_dir, 'src'), uri_list, args.jobs)
    print_details(workspace_dir, uri, lookup_name, lookup_track, lookup_database)


def print_details(workspace_dir, uri, lookup_name, lookup_track, lookup_database):
    console.pretty_println("\n***************************** Development Workspace ******************************", console.bold)
    console.pretty_print("Workspace: ", console.cyan)
    console.pretty_println(workspace_dir, console.yellow)
    if not uri:
        console.pretty_print("Sources  : ", console.cyan)
        console.pretty_println("empty workspace", console.yellow)
    elif lookup_name:
        console.pretty_println("Lookup Details: ", console.cyan)
        console.pretty_print("  Name    : ", console.cyan)
        console.pretty_println(lookup_name, console.yellow)
        console.pretty_print("  Track   : ", console.cyan)
        console.pretty_println(lookup_track, console.yellow)
        console.pretty_print("  Database: ", console.cyan)
        console.pretty_println(lookup_database, console.yellow)
        console.pretty_print("  Sources : ", console.cyan)
        console.pretty_println(uri, console.yellow)
    else:
        console.pretty_print("Sources  : ", console.cyan)
        console.pretty_println(uri, console.yellow)
    console.pretty_println("**********************************************************************************", console.bold)
    console.pretty_println("\nMerge additional source directories with `wstool` and configure parallel builds with 'yujin_init_build'.\n", console.cyan)
