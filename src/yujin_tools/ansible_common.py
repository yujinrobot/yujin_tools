##############################################################################
# Imports
##############################################################################

import argparse
import os
import termcolor
import yujin_ansible_playbooks

##############################################################################
# Methods
##############################################################################


def ansible_playbooks_home():
    """
    Root directory of where the ansible playbooks package may be found. If a
    dev has cloned the package elsewhere, there are other handles for overriding
    this value.

    :returns: path to the playbooks package
    """
    # return os.path.join(os.path.abspath(os.sep), "opt", "yujin", "ansible_playbooks")
    return os.path.join(yujin_ansible_playbooks.get_playbook_dir())

##############################################################################
# Arg Parsing
##############################################################################


def add_ansible_arguments(parser):
    """
    Any arguments for the parser that should be available for every single
    ansible call.

    :param argparse.ArgumentParser parser:
    """
    group = parser.add_argument_group(title="ansible arguments")
    group.add_argument('-v', '--verbose', action='store_true', help='execute the playbook with extra verbosity')
    group.add_argument('--home', action='store', default=ansible_playbooks_home(), help='path to the ansible playbooks home')


def add_devel_stable_arguments(parser):
    """
    Devel (default) or stable stream arguments for gopher software and docker images.

    :param argparse.ArgumentParser parser:
    """
    streams_group = parser.add_argument_group(title="stream arguments")
    group = streams_group.add_mutually_exclusive_group(required=False)
    group.add_argument('--devel', action='store_const', const='devel', dest='stream', default='devel', help='development stream')
    group.add_argument('--stable', action='store_const', const='stable', dest='stream', default='devel', help='stable stream')


def add_docker_arguments(parser):
    """
    Arguments relevant for a docker image.

    :param argparse.ArgumentParser parser:
    """
    group = parser.add_argument_group(title="docker arguments")
    group.add_argument('--only-image', action='store_true', help='only install/upgrade the docker image')


def add_gopher_software_arguments(parser):
    """
    Arguments relevant for a gopher software environment.

    :param argparse.ArgumentParser parser:
    """
    group = parser.add_argument_group(title="gopher software arguments")
    group.add_argument('--repository', default='internal', action='store', choices=['internal', 'external', 'partners'], help='only upgrade the gopher software binaries')
    group.add_argument('--only-upgrade', action='store_true', help='only upgrade the gopher software binaries')
    group.add_argument('--only-rosdeps', action='store_true', help='only do the --install-rosdeps step')
    group.add_argument('--skip-rosdeps', action='store_true', help='skip the --install-rosdeps step')


def add_ros_arguments(parser):
    """
    Arguments relevant for a ros system.

    :param argparse.ArgumentParser parser:
    """
    pass
#     group = parser.add_argument_group(title="ros arguments")
#     group.add_argument('--only-upgrade', action='store_true', help='only upgrade currently installed ros debians')
#     group.add_argument('--only-rosdeps', action='store_true', help='only do the --install-rosdeps step')
#     group.add_argument('--skip-rosdeps', action='store_true', help='skip the --install-rosdeps step')


##############################################################################
# Pretty Printing
##############################################################################


def colorise_key_value_pairs(key_value_strings, width=None):
    colorised = {}
    if width is None:
        width = max(len(k) for k in key_value_strings.keys())
    for key, value in key_value_strings.iteritems():
        colorised_key = termcolor.colored("{key:{width}}".format(key=key, width=width), "cyan")
        colorised_value = termcolor.colored(value, "yellow")
        colorised[colorised_key] = colorised_value
    return colorised


def pretty_print_key_value_pairs(title, key_value_strings, width=None):
    termcolor.cprint(title, "green")
    for k, v in colorise_key_value_pairs(key_value_strings, width).iteritems():
        print("  " + k + ": " + v)


def pretty_print_banner(title):
    width = 80
    print("")
    termcolor.cprint("*" * width, "green")
    termcolor.cprint("{text:^{width}}".format(text=title, width=width), "white", attrs=["bold"])
    termcolor.cprint("*" * width, "green")
    print("")

##############################################################################
# Ansible Command Formatting
##############################################################################


def append_verbosity_argument(cmd, verbosity):
    """
    Just in case we want to modify how many v's we use, centralise this here.
    """
    return cmd + " -vvvv" if verbosity else cmd

