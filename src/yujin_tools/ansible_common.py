##############################################################################
# Imports
##############################################################################

import os

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
