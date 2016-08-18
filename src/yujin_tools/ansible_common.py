##############################################################################
# Imports
##############################################################################

import os
import termcolor

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
    return os.path.join(os.path.abspath(os.sep), "opt", "yujin", "ansible_playbooks")


def add_ansible_arguments(parser):
    """
    Any arguments for the parser that should be available for every single
    ansible call.

    :param argparse.ArgumentParser parser:
    """
    parser.add_argument('-v', '--verbose', action='store_true', help='execute the playbook with extra verbosity')
    parser.add_argument('--home', action='store', default=ansible_playbooks_home(), help='path to the ansible playbooks home')


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
