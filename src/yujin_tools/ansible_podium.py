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
    Run all playbooks required to completely setup robot/concert podium
    simulations.
    """
    pass


def parse_docker_args(args, docker_name):
    """
    Runs the playbook for the specified docker.

    :param argparse.ArgumentParser args: args from a python argument parser
    :param str docker_name: name of the docker playbook to run.

    """
    ansible_common.pretty_print_banner("This is the 'podium-docker' play.")
    tags = ""
    cmd = "ansible-playbook concert-docker_{0}.yml --ask-become-pass --ask-vault-pass -i localhost, -c local -e yujin_stream=devel {1}".format(docker_name, tags)
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
    parsers = {}
    parsers['all'] = subparsers.add_parser("podium-all",
                                           description="Install/update everything for podium robot/concert simulations.",  # this shows in the help for this command
                                           help="run all playbooks required by podium simulations",  # this shows in the parent parser
                                           formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                           )
    ansible_common.add_devel_stable_arguments(parsers['all'])
    parsers['all'].set_defaults(func=parse_all_args)

    parsers['ros'] = subparsers.add_parser("podium-ros",
                                           description="Install/update ros software for podium simulations. Note that the requirements for the robot is subsumed by that of the concert, so this installs and updates the needs for both robot and concert.",  # this shows in the help for this command
                                           help="ros software for podium simulations (robot & concert)",  # this shows in the parent parser
                                           formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                           )
    ansible_common.add_devel_stable_arguments(parsers['ros'])
    ansible_common.add_gopher_software_arguments(parsers['ros'])
    parsers['ros'].set_defaults(func=parse_ros_args)

    for name in ['balcony', 'gateway', 'static']:
        parsers[name] = subparsers.add_parser("podium-{0}".format(name),
                                              description="Install/update the {0} docker for podium concrt simulations.".format(name),  # this shows in the help for this command
                                              help="{0} docker for podium concert simulations".format(name),  # this shows in the parent parser
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                              )
        ansible_common.add_devel_stable_arguments(parsers[name])
        ansible_common.add_docker_arguments(parsers[name])
        parsers[name].set_defaults(func=functools.partial(parse_docker_args, docker_name=name))

    for parser in parsers.values():
        ansible_common.add_ansible_arguments(parser)
