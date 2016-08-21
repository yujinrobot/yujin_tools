##############################################################################
# Imports
##############################################################################

import argparse
import subprocess

from . import ansible_common

##############################################################################
# Methods
##############################################################################


def parse_docker_args(args):
    """
    Starts the docker play for podiums.

    @todo parameterise internal/external and devel/stable
    """
    ansible_common.pretty_print_banner("This is the 'podium-docker' play.")
    if args.containers:
        tags = "--tags concert-containers"
    else:
        tags = "--tags concert-dockers"
    cmd = "ansible-playbook concert.yml --ask-become-pass --ask-vault-pass -i localhost, -c local -e yujin_stream=devel {0}".format(tags)
    cmd = ansible_common.append_verbosity_argument(cmd, args.verbose)
    ansible_common.pretty_print_key_value_pairs("Parameters", {"Stream": "devel"}, 10)
    ansible_common.pretty_print_key_value_pairs("Ansible", {"Command": cmd}, 10)
    print("")
    subprocess.call(cmd, cwd=args.home, shell=True)


def parse_ros_args(args):
    """
    Starts the ros play for podiums. Currently this is hardcoded to install
    the devel branch from the internal server. Since the requirements for
    the robot are subsumed by those for the concert, we only worry about
    runnign the concert playbook.

    @todo parameterise internal/external and devel/stable
    """
    ansible_common.pretty_print_banner("This is the 'podium-ros' play.")
    cmd = "ansible-playbook concert-ros_concert.yml  --ask-become-pass -i localhost, -c local -e yujin_internal=true -e yujin_stream=devel"
    cmd = ansible_common.append_verbosity_argument(cmd, args.verbose)
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

    docker_parser = subparsers.add_parser("podium-docker",
                                          description="Install/update concert dockers for podium simulations.",  # this shows in the help for this command
                                          help="concert dockers for the podium simulations",  # this shows in the parent parser
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                          )
    ansible_common.add_ansible_arguments(docker_parser)
    docker_parser.add_argument('--containers', action='store_true', help='only download/update the containers')
    docker_parser.set_defaults(func=parse_docker_args)
