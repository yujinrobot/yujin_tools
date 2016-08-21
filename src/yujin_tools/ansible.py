##############################################################################
# Imports
##############################################################################

import argparse
import subprocess
import sys

from . import ansible_common
from . import ansible_pc
from . import ansible_podium
from . import ansible_concert
from . import ansible_robot

##############################################################################
# Methods
##############################################################################


def _update():
    """
    Updates both ansible and the playbook package that are installed on the
    system. This will bootstrap ansible to the latest versio if it already
    hasn't done so.
    """
    cmd = "ansible-playbook pc-ansible.yml -K -i localhost, -c local"
    ansible_common.pretty_print_banner("Updating Playbooks and Tools")
    ansible_common.pretty_print_key_value_pairs("Ansible", {"Command": cmd})
    print("")
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
    parser = argparse.ArgumentParser(description='Ansible executor for installing/updating/configuring in a wild variety of systems.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)  # RawTextHelpFormatter for whitespace preservation

    # These aren't actually used, but we include them here so they get onto the help screen
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--version', action='store_true', help='Display the version of the installed yujin ansible playbooks package')
    group.add_argument('-u', '--update', action='store_true', help="Bootstrap yujin's ansible playbooks and python tools to the latest versions")

    subparsers = parser.add_subparsers(title='playbooks',
                                       help='name of an existing playbook',
                                       metavar="<playbook>")
    ansible_pc.add_subparser(subparsers)
    ansible_robot.add_subparser(subparsers)
    ansible_podium.add_subparser(subparsers)
    ansible_concert.add_subparser(subparsers)
    options, unused_unknown_args = parser.parse_known_args(args)

    options.func(options)  # relay arg parsing to the subparser configured `set_defaults` function callback
