#!/usr/bin/env python
#from distutils.core import setup
#import sys

# Setuptools' sdist does not respect package_data
#from setuptools import setup, find_packages
from distutils.core import setup

import sys
sys.path.insert(0, 'src')

from yujin_tools import __version__

setup(name='yujin_tools',
      version= __version__,
      packages=['yujin_tools', 'catkin_make'],
      package_dir = {'yujin_tools':'src/yujin_tools', 'catkin_make':'src/catkin_make'},
      scripts = [
           'scripts/cfind',
           'scripts/avahi-browse-concerts',
           'scripts/avahi-browse-multimaster',
           'scripts/git-big-picture',
           'scripts/dslam_binaries',
           'scripts/groot_binaries',
           'scripts/groot_sources',
           'scripts/groot_build',
           'scripts/groot_sync',
           'scripts/masteruri',
           'scripts/yujin_add_to_users_group',
           'scripts/yujin_ascii_plot',
           'scripts/yujin_init_workspace',
           'scripts/yujin_init_build',
           'scripts/yujin_make',
           'scripts/yujin_make_isolated',
           'scripts/yujin_tools_settings',
           'scripts/yujin_tools_update',
           'scripts/yujin_list_git_branches',
      ],
      package_data = {'yujin_tools': [
           'cmake/*',
           'templates/init_build/.bashrc',
           'templates/init_build/konsole',
           'templates/init_build/gnome-terminal',
           'templates/init_build/eclipse',
           'templates/init_build/android-studio',
           'toolchains/buildroot/*',
           'toolchains/ubuntu/*',
           'toolchains/code_sourcery/*',
	   'toolchains/nexell/*',
           'platforms/default.cmake',
           'platforms/generic/*',
           'platforms/arm/*',
           'platforms/intel/*',
           'data/*'
           ]},
      author = "Daniel Stonier",
      author_email = "d.stonier@gmail.com",
      maintainer='Daniel Stonier',
      url = "http://pypi.python.org/pypi/yujin_tools",
      download_url = "https://github.com/yujinrobot/yujin_tools.git",
      keywords = ["Yujin Robot"],
      classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License" ],
      description = "Utilities for yujin's development environment",
      long_description = "Refer to the documentation at https://github.com/yujinrobot/yujin_tools.",
      license = "BSD"
#      install_requires=[
#        'argparse',
        #'python-catkin-pkg',
#    ],
      )

# This no longer works...it has to be a special parsable syntax of pypi's.
#      long_description = open('README.md').read(),

