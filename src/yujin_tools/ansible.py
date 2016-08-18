##############################################################################
# Imports
##############################################################################

import argparse
import subprocess
import sys
import termcolor

from . import ansible_common
from . import ansible_pc

##############################################################################
# Methods
##############################################################################


def _update():
    """
    Updates both ansible and the playbook package that are installed on the
    system.
    """
    # should perhaps try and find some way of checking that ansible is already
    # setup by yujin_ansible_bootstrap
    termcolor.cprint("********************************************************************************", "green")
    termcolor.cprint("               Updating Yujin's ansible playbooks and scripts", "green")
    termcolor.cprint("********************************************************************************\n", "green")
    cmd = "ansible-playbook pc-ansible.yml -K -i localhost, -c local"
    print("{0}: {1}\n".format(termcolor.colored("Command", "cyan"),
                              termcolor.colored(cmd, "yellow")))
    subprocess.call(cmd, cwd=ansible_common.ansible_playbooks_home(), shell=True)


def main(args=sys.argv[1:]):
    # Manually handle exclusive options first since subparsers can't be 'optional'.
    if len(sys.argv) == 2 and sys.argv[1] == "--version":
        print("Version: TODO")
        return
    if len(sys.argv) == 2 and sys.argv[1] == "--update":
        _update()
        return

    # TODO check that yujin_ansible_bootstrap has already been executed, and if not - execute and exit with a friendly message
    parser = argparse.ArgumentParser(description='Executor for ansible playbooks in a wild variety of situations.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)  # RawTextHelpFormatter for whitespace preservation

    # These aren't actually used, but we include them here so they get onto the help screen
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--version', action='store_true', help='Display the version of the installed yujin ansible playbooks package')
    group.add_argument('-u', '--update', action='store_true', help='Make sure you have the latest playbooks')

    subparsers = parser.add_subparsers(title='playbooks',
                                       help='name of an existing playbook',
                                       metavar="<playbook>")
    ansible_pc.add_subparser(subparsers)
    options, unused_unknown_args = parser.parse_known_args(args)
    options.func(options)  # relay arg parsing to the subparser configured `set_defaults` function callback
