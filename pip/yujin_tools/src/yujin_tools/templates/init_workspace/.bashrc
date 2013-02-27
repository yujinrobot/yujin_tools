#!/bin/bash
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
if [ -f ~/.profile ]; then
  . ~/.profile
fi
source %(overlay)s/setup.bash
export YUJIN_WORKSPACE=%(cwd)s
