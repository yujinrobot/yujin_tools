##############################################################################
# Imports
##############################################################################

import os.path

import sys

import subprocess
import argparse
import shutil
from catkin_pkg.packages import find_packages

##############################################################################
# Local imports
##############################################################################

import common
import console
import make 

import catkin_make.terminal_color as terminal_color
from catkin_make.terminal_color import fmt

##############################################################################
# Methods
##############################################################################

def _parse_args(args=sys.argv[1:]):

    parser = argparse.ArgumentParser(description='Generates the documents for packages in the workspace.')
    parser.add_argument('-p', '--pre-clean', action='store_true', help='Clean build temporaries before making [false]')
    parser.add_argument('--no-color', action='store_true', help='Disables colored ouput')
# TODO: Threading   parser.add_argument('-j', '--jobs', type=int, metavar='JOBS', default=None, nargs='?', help='Specifies the number of jobs (commands) to run simultaneously. Defaults to the environment variable ROS_PARALLEL_JOBS and falls back to the number of CPU cores.')

# TODO: specifiying output directory
#    parser.add_argument('-o', '--output',  

    options, unknown_args = parser.parse_known_args(args)

    return options

def generate_doc(name, pkg_path, doc_path):
    document_path = doc_path + '/' + name
    args = ['rosdoc_lite', '-o', document_path, pkg_path]
    output = subprocess.call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output

def output(fd, html):
    for h in html:
        os.write(fd, h)
        os.write(fd,'\n')

def generates_index_page(doc_path, pkg_names):

    index_page = doc_path + '/index.html'
    fd = os.open(index_page, os.O_RDWR | os.O_CREAT)

    html_header = ['<!DOCTYPE html>',
                   '<html>         ',
                   '  <head>       ',
                   '    <meta charset="UTF-8"/>',
                   '    <title> Documents </title>',
                   '  </head>      ',
                   '  <body>       ',
                   '    <h1> Package Lists </h1>',
                  ]

    html_footer = [
                   '  </body>                     ',
                   '</html>                       ',
                   ]

    output(fd, html_header)

    for pkg in pkg_names:
        link_html = '  <p><a href="' + pkg + '/html/index.html">' + pkg + '</a></p>'
        output(fd, [link_html])

    output(fd, html_footer)
    os.close(fd)

def doc_make_main():
    args = _parse_args()

    if args.no_color:
        terminal_color.disable_ANSI_colors()

    (base_path, build_path, devel_path, source_path, doc_path) = common.get_default_paths()

    make.validate_build_space(base_path)

    # Clear out previous temporaries if requested
    if args.pre_clean:
        console.pretty_print("Pre-cleaning before building.", console.cyan)
        shutil.rmtree(doc_path, ignore_errors=True)

    if not os.path.exists(doc_path):
        os.mkdir(doc_path)

    # ensure toplevel cmake file exists
    toplevel_cmake = os.path.join(source_path, 'CMakeLists.txt')
    if not os.path.exists(toplevel_cmake):
        return fmt('@{rf}No toplevel cmake file@')

    # did source paths get added to the original location?
    make.check_and_update_source_repo_paths(source_path)

    # list up packages with its absolute path
    packages = find_packages(source_path, exclude_subspaces=True)
    packages_by_name = {p.name: source_path + '/' + path  for path, p in packages.iteritems()}

    # Help find catkin cmake and python
    unused_catkin_toplevel, catkin_python_path, unused_catkin_cmake_path = common.find_catkin(base_path)
    pkg_config_paths = common.generate_pkg_config_path(base_path)
    env = os.environ.copy() 
    sys.path.append(catkin_python_path)

    # PKG_CONFIG_PATH
    for path in pkg_config_paths:
        try:
            env['PKG_CONFIG_PATH'] = env['PKG_CONFIG_PATH'] + os.pathsep + path
        except KeyError:
            env['PKG_CONFIG_PATH'] = path 

    doc_output = {}
    for name, path in packages_by_name.items():
        print 'Generate doc for ' + name
        output = generate_doc(name, path, doc_path)
        doc_output[name] = output

    generates_index_page(doc_path, packages_by_name.keys())

    console.pretty_println('Document generation result. 0 may mean error. It is ok, most of time')
    for name, err in doc_output.items():
        console.pretty_print(name, console.cyan)
        console.pretty_print(' : ')
        console.pretty_println(str(err)) 
