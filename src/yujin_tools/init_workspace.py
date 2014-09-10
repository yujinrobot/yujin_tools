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
    parser.add_argument('-m', '--merge', action='store', default=None, help='merge a keyed (--list-rosinstall) rosinstall into the current workspace')
    parser.add_argument('--track', action='store', default=None, help='retrieve rosinstalls relevant to this track %s[%s]' % (settings.VALID_TRACKS, settings.DEFAULT_TRACK))
    parser.add_argument('-j', '--jobs', action='store', default=1, help='how many parallel threads to use for installing[1]')
    parser.add_argument('uri', nargs=argparse.REMAINDER, default=None, help='uri for a rosinstall file [None]')
    args = parser.parse_args()
    return args


def populate_workspace(base_path, uri_list, parallel_jobs, do_init=True):
    '''
      :param str base_path: location of the wstool workspace
      :param uri_list: list of uri's to rosinstall files
      :type uri_list: list of str
      :param bool do_init: whether to initialise the workspace first or just merge
    '''
    if do_init:
        wstool_arguments = ['wstool',
                            'init',
                            '-j %s' % str(parallel_jobs),
                            base_path,
                            ]
        wstool.wstool_cli.wstool_main(wstool_arguments)
    for uri in uri_list:
        wstool_arguments = ['wstool',
                            'merge',
                            '--target-workspace=%s' % base_path
                        ]
        wstool_arguments.append(uri)
        wstool.wstool_cli.wstool_main(wstool_arguments)
    # update
    wstool_arguments = ['wstool',
                        'update',
                        '-j %s' % str(parallel_jobs),
                        '--target-workspace=%s' % base_path
                    ]
    wstool.wstool_cli.wstool_main(wstool_arguments)


def list_rosinstalls(track):
    response = urllib2.urlopen('%s/%s.yaml' % (settings.get_rosinstall_database_uri(), track))
    rosinstalls = yaml.load(response.read())
    sorted_rosinstalls = rosinstalls.keys()
    sorted_rosinstalls.sort()
    for r in sorted_rosinstalls:
        console.pretty_print(" " + r + ": ", console.cyan)
        console.pretty_println("%s" % rosinstalls[r], console.yellow)


def get_rosinstall_database(track):
    lookup_track = track
    lookup_database = settings.get_rosinstall_database_uri()
    response = urllib2.urlopen('%s/%s.yaml' % (lookup_database, track))
    rosinstall_database = yaml.load(response.read())
    return rosinstall_database, lookup_track, lookup_database


def parse_database(search_names, rosinstall_database):
    names = []
    sources = []
    for name in search_names:
        if name in rosinstall_database:
            elements = rosinstall_database[name]
            new_names = []
            new_sources = []
            if type(elements) is list:
                for element in elements:
                    if element.endswith('.rosinstall'):
                        new_sources.append(element)
                    else:
                        new_names.append(element)
            else:  # single entry
                if elements.endswith('.rosinstall'):
                    new_sources.append(elements)
                else:
                    new_names.append(elements)
            names.extend(new_names)
            sources.extend(new_sources)
            if new_names:
                (new_names, new_sources) = parse_database(new_names, rosinstall_database)
                names.extend(new_names)
                sources.extend(new_sources)
        else:
            raise RuntimeError("not found in the rosinstall database [%s]" % name)
#                    (new_names, new_sources) = parse_database([elements], rosinstall_database)
#                        (new_names, new_sources) = parse_database([element], rosinstall_database)
#                        names.extend(new_names)
#                        sources.extend(new_sources)
#                    sources.append(elements)
#                    names.extend(new_names)
#                    sources.extend(new_sources)
    return (names, sources)


def merge(key, track, jobs):
    '''
      Merge a rosinstall into the workspace. The key can either be an

      - absolute path to a rosinstall file
      - name of a rosinstall file in the current dir
      - key in the rosinstall database

      :param str key: see above
      :param str track: the track to pull keys from (e.g. hydro, indigo)
      :param str jobs: number of parallel download jobs to spawn via wstool
    '''
    if os.environ.get('YUJIN_WORKSPACE') is not None:
        workspace_dir = os.environ.get('YUJIN_WORKSPACE')
    elif os.path.isdir(os.path.join(os.getcwdu(), 'src')):
        workspace_dir = os.getcwdu()
    elif os.path.isfile(os.path.join(os.getcwdu(), '.rosinstall')):
        workspace_dir = os.path.join(os.getcwdu(), '..')
    else:
        raise RuntimeError("Could not find an initialised workspace (you must be at the root below 'src', or in a setup.bash'd environment)")
    uri_list = []
    if os.path.isabs(key):
        uri_list.append(key)
    elif os.path.isfile(os.path.join(os.getcwd(), key)):
        uri_list.append(os.path.join(os.getcwdu(), key))
    elif urlparse.urlparse(key).scheme == "":  # not a http element, let's look up our database
        rosinstall_database, unused_lookup_track, unused_lookup_database = get_rosinstall_database(track)
        (unused_database_name_list, database_uri_list) = parse_database([key], rosinstall_database)
        uri_list.extend(database_uri_list)
    else:  # it's a http element'
        uri_list.append(key)
    populate_workspace(os.path.join(workspace_dir, 'src'), uri_list, jobs, do_init=False)


def init_workspace():
    '''
      Process the init workspace command and return success or failure to the calling script.
    '''
    args = parse_arguments()
    if not args.track:
        args.track = settings.get_default_track()
    if args.list_rosinstalls:
        list_rosinstalls(args.track)
        return 0
    if args.merge is not None:
        merge(args.merge, args.track, args.jobs)
        return 0
    if os.path.isabs(args.dir):
        workspace_dir = args.dir
    else:
        workspace_dir = os.path.join(os.getcwd(), args.dir)
    if not os.path.isdir(workspace_dir):
        os.mkdir(workspace_dir)
    if os.path.isdir(os.path.join(workspace_dir, 'src')):
        raise RuntimeError("This workspace is already initialised")
    uri_list = []
    lookup_name_list = []
    for uri in args.uri:
        if os.path.isabs(uri):
            uri_list.append(uri)
        elif os.path.isfile(os.path.join(os.getcwd(), uri)):
                uri_list.append(os.path.join(os.getcwd(), uri))
        elif urlparse.urlparse(uri).scheme == "":  # not a http element, let's look up our database
                lookup_name_list.append(uri)
        else:  # it's a http element'
            uri_list.append(uri)
    rosinstall_database, lookup_track, lookup_database = get_rosinstall_database(args.track)
    (database_name_list, database_uri_list) = parse_database(lookup_name_list, rosinstall_database)
    lookup_name_list.extend(database_name_list)
    uri_list.extend(database_uri_list)
    populate_workspace(os.path.join(workspace_dir, 'src'), uri_list, args.jobs)
    print_details(workspace_dir, uri_list, lookup_name_list, lookup_track, lookup_database)
    return 0


def print_details(workspace_dir, uri_list, lookup_name_list, lookup_track, lookup_database):
    console.pretty_println("\n***************************** Development Workspace ******************************", console.bold)
    console.pretty_print("Workspace   : ", console.cyan)
    console.pretty_println(workspace_dir, console.yellow)
    if lookup_name_list:
        console.pretty_print("  Names     : ", console.cyan)
        for lookup_name in lookup_name_list:
            console.pretty_print("%s " % lookup_name, console.yellow)
        console.pretty_println('', console.yellow)
        console.pretty_print("    Track   : ", console.cyan)
        console.pretty_println(lookup_track, console.yellow)
        console.pretty_print("    Database: ", console.cyan)
        console.pretty_println(lookup_database, console.yellow)
    console.pretty_print("  Sources   : ", console.cyan)
    if uri_list:
        console.pretty_println("%s " % uri_list[0], console.yellow)
        for uri in uri_list[1:]:
            console.pretty_print("            : ", console.cyan)
            console.pretty_println("%s " % uri, console.yellow)
    else:
        console.pretty_println("empty workspace", console.yellow)
    console.pretty_println("**********************************************************************************", console.bold)
    console.pretty_println("\nMerge additional source directories with `wstool` and configure parallel builds with 'yujin_init_build'.\n", console.cyan)
