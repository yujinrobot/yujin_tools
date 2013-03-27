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
      packages=['yujin_tools'],
      package_dir = {'yujin_tools':'src/yujin_tools'},
      scripts = ['scripts/cfind',
           'scripts/yujin_init_workspace',
           'scripts/yujin_init_build',
           'scripts/roscreate-shortcuts',
           'scripts/yujin_toolchain',
           'scripts/yujin_platform',
      ],
      package_data = {'yujin_tools': [
           'cmake/*',
           'templates/init_build/Makefile',
           'templates/init_build/.bashrc',
           'templates/init_build/konsole',
           'templates/init_build/gnome-terminal',
           'templates/init_build/eclipse',
           'toolchains/arm-generic-gnueabi.cmake',
           'platforms/arm1176jzf-s.cmake' 
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
      )

# This no longer works...it has to be a special parsable syntax of pypi's.
#      long_description = open('README.md').read(),

