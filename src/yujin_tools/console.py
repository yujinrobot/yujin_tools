#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/yujinrobot/yujin_tools/master/LICENSE
#

##############################################################################
# Imports
##############################################################################

import sys

##############################################################################
# Methods
##############################################################################


def console_has_colours(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False  # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False

has_colours = console_has_colours(sys.stdout)
#reset = "\x1b[0;0m"
reset = "\x1b[0m"

bold = '1'
black, red, green, yellow, blue, magenta, cyan, white = [str(i) for i in range(30, 38)]
bold_black, bold_red, bold_green, bold_yellow, bold_blue, bold_magenta, bold_cyan, bold_white = ['1;' + str(i) for i in range(30, 38)]
colours = [
           bold,
           black, red, green, yellow, blue, magenta, cyan, white,
           bold_black, bold_red, bold_green, bold_yellow, bold_blue, bold_magenta, bold_cyan, bold_white
          ]


def pretty_print(msg, colour=white):
    if has_colours:
        seq = "\x1b[%sm" % (colour) + msg + reset
        sys.stdout.write(seq)
    else:
        sys.stdout.write(msg)


def pretty_println(msg, colour=white):
    if has_colours:
        seq = "\x1b[%sm" % (colour) + msg + reset
        sys.stdout.write(seq)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(msg)


##############################################################################
# Console
##############################################################################


def debug(msg):
    pretty_print("%s\n" % msg, green)


def warning(msg):
    pretty_print("%s\n" % msg, yellow)


def error(msg):
    pretty_print("%s\n" % msg, red)


def logdebug(message):
    pretty_print("[debug] " + message + "\n", green)


def logwarn(message):
    pretty_print("[warning] " + message + "\n", yellow)


def logerror(message):
    pretty_print("[error] " + message + "\n", red)


def logfatal(message):
    pretty_print("[error] " + message + "\n", bold_red)


##############################################################################
# Main
##############################################################################

if __name__ == '__main__':
    for colour in colours:
        pretty_print("dude\n", colour)
    logdebug("info message")
    logwarn("warning message")
    logerror("error message")
    logfatal("fatal message")
    pretty_print("red\n", red)
    print("some normal text")