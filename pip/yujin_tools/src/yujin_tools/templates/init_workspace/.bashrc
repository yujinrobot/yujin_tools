#!/bin/bash
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
if [ -f ~/.profile ]; then
  . ~/.profile
fi
source /opt/ros/groovy/setup.bash
