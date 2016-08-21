##############################################################################
# Imports
##############################################################################

import argparse
import functools
import subprocess

from . import ansible_common

##############################################################################
# Methods
##############################################################################


def parse_all_args(args):
    """
    Run all playbooks required to completely setup a robot.
    """
    ansible_common.pretty_print_banner("This is the 'robot-all' play.")
    print("Coming soon...")


def parse_ros_args(args):
    """
    Starts the ros play for podiums. Currently this is hardcoded to install
    the devel branch from the internal server. Since the requirements for
    the robot are subsumed by those for the concert, we only worry about
    runnign the concert playbook.
    """
    ansible_common.pretty_print_banner("This is the 'robot-gopher' play.")
    print("Coming soon...")


def add_subparser(subparsers):
    """
    Add our own argparser to the parent.

    :param subparsers: the subparsers factory from the parent argparser.
    """
    parsers = {}
    parsers['all'] = subparsers.add_parser("robot-all",
                                           description="Install/update everything for a robot.",  # this shows in the help for this command
                                           help="run all playbooks required by a robot",  # this shows in the parent parser
                                           formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                           )
    ansible_common.add_devel_stable_arguments(parsers['all'])
    parsers['all'].set_defaults(func=parse_all_args)

    parsers['ros'] = subparsers.add_parser("robot-gopher",
                                           description="Install/update gopher software for the robot.",  # this shows in the help for this command
                                           help="gopher software for the robot",  # this shows in the parent parser
                                           formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                           )
    ansible_common.add_devel_stable_arguments(parsers['ros'])
    ansible_common.add_gopher_software_arguments(parsers['ros'])
    parsers['ros'].set_defaults(func=parse_ros_args)

    for parser in parsers.values():
        ansible_common.add_ansible_arguments(parser)
