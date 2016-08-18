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
    Starts the ros play for podiums. Currently this is hardcoded to install
    the devel branch from the internal server. Since the requirements for
    the robot are subsumed by those for the concert, we only worry about
    runnign the concert playbook.

    @todo parameterise internal/external and devel/stable
    """
    ansible_common.pretty_print_banner("This is the 'podium-ros_concert' play.")
    cmd = "ansible-playbook concert-ros_concert.yml -K -i localhost, -c local -e yujin_internal=true -e yujin_stream=devel"
    if args.verbose:
        cmd += " -vvv"
    ansible_common.pretty_print_key_value_pairs("Parameters", {"Location": "internal", "Stream": "devel"}, 10)
    ansible_common.pretty_print_key_value_pairs("Ansible", {"Command": cmd}, 10)
    print("")
    subprocess.call(cmd, cwd=args.home, shell=True)


def add_subparser(subparsers):
    """
    Add our own argparser to the parent.

    :param subparsers: the subparsers factory from the parent argparser.
    """
    ros_parser = subparsers.add_parser("podium-ros",
                                       description="Install/update ros software for podium simulations. Note that the requirements for the robot is subsumed by that of the concert, so this installs and updates the needs for both robot and concert.",  # this shows in the help for this command
                                       help="ros software for podium simulations (robot & concert)",  # this shows in the parent parser
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                       )
    ansible_common.add_ansible_arguments(ros_parser)
    ros_parser.set_defaults(func=parse_ros_args)
