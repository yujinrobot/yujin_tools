#!/usr/bin/env python
#from distutils.core import setup
#import sys

# Setuptools' sdist does not respect package_data
# from setuptools import setup, find_packages
# Distutils however, does not respect install_requires
# Distutils is in python, setuptools is outside
# Setuptools is now the defacto default though
#try:
#    from setuptools import setup
#except ImportError:
#    from distutils.core import setup
from distutils.core import setup

import sys
sys.path.insert(0, 'src')

from yujin_tools.version import __version__

setup(name='yujin_tools',
      version= __version__,
      packages=['yujin_tools', 'catkin_make'],
      package_dir = {'yujin_tools':'src/yujin_tools', 'catkin_make':'src/catkin_make'},
      scripts = [
           'scripts/cfind',
           'scripts/avahi-browse-concerts',
           'scripts/avahi-browse-multimaster',
           'scripts/groot_start_concert',
           'scripts/groot_start_robot',
           'scripts/groot_binaries',
           'scripts/groot_arm_binaries',
           'scripts/groot_sources',
           'scripts/groot_sync',
           'scripts/masteruri',
           'scripts/yujin_add_to_users_group',
           'scripts/yujin_ascii_plot',
           'scripts/yujin_ansible_bootstrap',
           'scripts/yujin_clean_pyc_files',
           'scripts/yujin_init_workspace',
           'scripts/yujin_init_build',
           'scripts/yujin_make',
           'scripts/yujin_make_isolated',
           'scripts/yujin_tools_settings',
           'scripts/yujin_list_dirs_by_size',
           'scripts/yujin_list_git_branches',
           'scripts/yujin_upload_deb',
           'scripts/rosdep-generator',
           # 'scripts/yujin_release',
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
      license = "BSD",
      # not picked up by distutils, need to install setuptools above
      # but even then I'm not getting much happening
      # install_requires = [
      #     'pyyaml',
      #     'python-catkin-pkg',
      # ],
      )

# This no longer works...it has to be a special parsable syntax of pypi's.
#      long_description = open('README.md').read(),

