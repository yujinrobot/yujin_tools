##############################################################################
# Imports
##############################################################################

import argparse
import subprocess

from . import ansible_common

##############################################################################
# Methods
##############################################################################


def parse_ros_args(args):
    """
    Launches the playbooks for managing the ros software environment on a pc.
    """
    ansible_common.pretty_print_banner("'pc-ros'")
    cmd = "ansible-playbook pc-ros.yml -K -i localhost, -c local"
    cmd = ansible_common.append_verbosity_argument(cmd, args.verbose)
    ansible_common.pretty_print_key_value_pairs("Ansible", {"Command": cmd}, 10)
    print("")
    subprocess.call(cmd, cwd=args.home, shell=True)


def parse_gopher_args(args):
    """
    Launches the playbooks for managing the gopher software environment on a pc.
    """
    ansible_common.pretty_print_banner("'pc-gopher'")
    cmd = "ansible-playbook pc-gopher_software.yml -K -i localhost, -c local -e yujin_repository={0} -e yujin_stream={1}".format(args.repository, args.stream)
    cmd = ansible_common.append_verbosity_argument(cmd, args.verbose)
    ansible_common.pretty_print_key_value_pairs("Parameters", {"Repository": args.repository, "Stream": args.stream}, 10)
    ansible_common.pretty_print_key_value_pairs("Ansible", {"Command": cmd}, 10)
    print("")
    subprocess.call(cmd, cwd=args.home, shell=True)


def add_subparser(subparsers):
    """
    Add our own argparser to the parent.

    :param subparsers: the subparsers factory from the parent argparser.
    """
    parsers = {}
    parsers['ros'] = subparsers.add_parser("pc-ros",
                                           description="Install, configure or update an existing ros distro.",  # this shows in the help for this command
                                           help="ros distro on an ubuntu machine",  # this shows in the parent parser
                                           formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                           )
    ansible_common.add_ros_arguments(parsers['ros'])
    parsers['ros'].set_defaults(func=parse_ros_args)

    parsers['gopher'] = subparsers.add_parser("pc-gopher",
                                              description="""
                                              Setup and maintain the complete development/runtime environment for
                                              gopher software development. This includes the underlying ros system,
                                              yujin apt repos, and the gopher software itself.
                                              """,  # this shows in the help for this command
                                              help="dev/runtime environment for the gopher software stack",  # this shows in the parent parser
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                              )
    ansible_common.add_devel_stable_arguments(parsers['gopher'])
    ansible_common.add_gopher_software_arguments(parsers['gopher'])
    parsers['gopher'].set_defaults(func=parse_gopher_args)

    for parser in parsers.values():
        ansible_common.add_ansible_arguments(parser)

#     parser = argparse.ArgumentParser(description='Executor for ansible playbooks on a pc.',
#                                      epilog=show_epilog(),
#                                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)  # RawTextHelpFormatter for whitespace preservation
#     parser.add_argument('-j', '--jobs', type=int, metavar='JOBS', default=None, nargs='?', help='Specifies the number of jobs (commands) to run simultaneously. Defaults to the environment variable ROS_PARALLEL_JOBS and falls back to the number of CPU cores.')
#     parser.add_argument('--force-cmake', action='store_true', help='Invoke "cmake" even if it has been executed before [false]')
#     parser.add_argument('-p', '--pre-clean', action='store_true', help='Clean build temporaries before making [false]')
#     parser.add_argument('-c', '--cmake-only', action='store_true', help='Do not compile, just force a re-run of cmake [false]')
#     group = parser.add_mutually_exclusive_group()
#     group.add_argument('-i', '--install', action='store_true', help='Run install step after making [false]')
#     group.add_argument('--track', choices=settings.VALID_TRACKS, dest='default_underlay', action='store', default=None, help='convenience equivalent for the --default-underlay option')
#     group.add_argument('--install-rosdeps-track', choices=settings.VALID_TRACKS, action='store', default=None, help='Install all rosdeps for the workspace sources and given track [None]')
#     group.add_argument('--install-rosdeps', action='store_true', help='Install all rosdeps for the workspace sources and track set by `yujin_tools_settings --get-default-track` [false]')
#     group.add_argument('-t', '--tests', action='store_true', help='Make tests [false]')
#     group.add_argument('-r', '--run-tests', action='store_true', help='Run tests (does not build them) [false]')
#     parser.add_argument('--strip', action='store_true', help='Strips binaries, only valid with --install')
#     parser.add_argument('--no-color', action='store_true', help='Disables colored ouput')
#     parser.add_argument('--target', default=None, help='Build against a particular target only')
#     parser.add_argument('--pkg', help='Invoke "make" on a specific package only')
#     parser.add_argument('--cmake-args', dest='cmake_args', nargs='*', type=str,
#         help='Arbitrary arguments which are passes to CMake. It must be passed after other arguments since it collects all following options.')
#     parser.add_argument('--make-args', dest='make_args', nargs='*', type=str,
#         help='Arbitrary arguments which are passes to make. It must be passed after other arguments since it collects all following options. This is only necessary in combination with --cmake-args since else all unknown arguments are passed to make anyway.')
