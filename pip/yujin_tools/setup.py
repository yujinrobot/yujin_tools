from distutils.core import setup

import sys
sys.path.insert(0, 'src')

from yujin_tools import __version__

setup(name='yujin_tools',
      version= __version__,
      packages=['yujin_tools'],
      package_dir = {'':'src'},
      scripts = ["scripts/cfind","scripts/yujin_init_workspace"],
      package_data = {'yujin_tools': [
           'templates/init_workspace/Makefile',
           'templates/init_workspace/.bashrc',
           'templates/init_workspace/konsole',
           'templates/init_workspace/gnome-terminal',
           'templates/init_workspace/eclipse',
           'templates/init_workspace/setup.bash',
           ]},
      author = "Daniel Stonier",
      author_email = "d.stonier@gmail.com",
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

