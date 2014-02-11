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
from make_doc_html_templates import html_header, html_footer

import catkin_make.terminal_color as terminal_color
from catkin_make.terminal_color import fmt

##############################################################################
# Methods
##############################################################################

DOC_PROGRAM = 'rosdoc_lite'


def generate_doc(name, pkg_path, doc_path):
    document_path = doc_path + '/' + name
    args = [DOC_PROGRAM, '-o', document_path, pkg_path]
    output = subprocess.call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output


def output(fd, html):
    for h in html:
        os.write(fd, h)
        os.write(fd, '\n')


def generates_index_page(doc_path, pkg_names):

    index_page = doc_path + '/index.html'
    fd = os.open(index_page, os.O_RDWR | os.O_CREAT)

    output(fd, html_header)

    for pkg in pkg_names:
        link_html = '  <p><a href="' + pkg + '/html/index.html">' + pkg + '</a></p>'
        output(fd, [link_html])

    output(fd, html_footer)
    os.close(fd)


def make_doc(source_path, doc_path, packages):

    if not common.which(DOC_PROGRAM):
        console.error('[' + DOC_PROGRAM + '] is not available.')
        console.error('Please make sure [' + DOC_PROGRAM + '] is in your python path')
        return

    if not os.path.exists(doc_path):
        os.mkdir(doc_path)

    # List up packages with its absolute path
    packages_by_name = {p.name: source_path + '/' + path for path, p in packages.iteritems()}

    doc_output = {}
    console.pretty_println('Generating documents in ' + doc_path, console.cyan)
    for name, path in packages_by_name.items():
        console.pretty_println('  ' + name)
        output = generate_doc(name, path, doc_path)
        doc_output[name] = output

    generates_index_page(doc_path, packages_by_name.keys())

    console.pretty_println('')
    console.pretty_println('Document generation result. 0 may mean error. But it is fine most of time', console.bold_white)
    for name, err in doc_output.items():
        console.pretty_print(name, console.cyan)
        console.pretty_print(' : ')
        console.pretty_println(str(err))
