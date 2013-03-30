# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

##############################################################################
# Imports
##############################################################################

import io
import os
import subprocess
import sys
import stat
try:
    from catkin_pkg.cmake import configure_file, get_metapackage_cmake_template_path
except ImportError as e:
    sys.exit(
        'ImportError: "from catkin_pkg.topological_order import '
        'topological_order" failed: %s\nMake sure that you have installed '
        '"catkin_pkg", it is up to date and on the PYTHONPATH.' % e
    )

##############################################################################
# Local Imports
##############################################################################

from .terminal_color import ansi, fmt, sanitize

##############################################################################
# Methods
##############################################################################


def split_arguments(args, splitter_name, default=None):
    if splitter_name not in args:
        return args, default
    index = args.index(splitter_name)
    return args[0:index], args[index + 1:]


def extract_cmake_and_make_arguments(args):
    cmake_args = []
    make_args = []
    if '--cmake-args' in args and '--make-args' in args:
        cmake_index = args.index('--cmake-args')
        make_index = args.index('--make-args')
        # split off last argument group first
        if cmake_index < make_index:
            args, make_args = split_arguments(args, '--make-args')
            args, cmake_args = split_arguments(args, '--cmake-args')
        else:
            args, cmake_args = split_arguments(args, '--cmake-args')
            args, make_args = split_arguments(args, '--make-args')
    elif '--cmake-args' in args:
        args, cmake_args = split_arguments(args, '--cmake-args')
    elif '--make-args' in args:
        args, make_args = split_arguments(args, '--make-args')

    # classify -D* and -G* arguments as cmake specific arguments
    implicit_cmake_args = [a for a in args if a.startswith('-D') or a.startswith('-G')]
    args = [a for a in args if a not in implicit_cmake_args]

    return args, implicit_cmake_args + cmake_args, make_args


def cprint(msg, end=None):
    print(fmt(msg), end=end)


def colorize_line(line):
    cline = sanitize(line)
    cline = cline.replace(
        '-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',
        '-- @{pf}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~@|'
    )
    if line.startswith('-- ~~'):
        # -- ~~  -
        cline = cline.replace('~~ ', '@{pf}~~ @|')
        cline = cline.replace(' - ', ' - @!@{bf}')
        cline = cline.replace('(', '@|(')
        cline = cline.replace('(plain cmake)', '@|(@{rf}plain cmake@|)')
        cline = cline.replace('(unknown)', '@|(@{yf}unknown@|)')
    if line.startswith('-- +++'):
        # -- +++ add_subdirectory(package)
        cline = cline.replace('+++', '@!@{gf}+++@|')
        cline = cline.replace('kin package: \'', 'kin package: \'@!@{bf}')
        cline = cline.replace(')', '@|)')
        cline = cline.replace('\'\n', '@|\'\n')
        cline = cline.replace('cmake package: \'', 'cmake package: \'@!@{bf}')
        cline = cline.replace('\'\n', '@|\'\n')
    if line.startswith('-- ==>'):
        cline = cline.replace('-- ==>', '-- @!@{bf}==>@|')
    if line.lower().startswith('warning'):
        # WARNING
        cline = ansi('yf') + cline
    if line.startswith('CMake Warning'):
        # CMake Warning...
        cline = cline.replace('CMake Warning', '@{yf}@!CMake Warning@|')
    if line.startswith('ERROR:'):
        # ERROR:
        cline = cline.replace('ERROR:', '@!@{rf}ERROR:@|')
    if line.startswith('CMake Error'):
        # CMake Error...
        cline = cline.replace('CMake Error', '@{rf}@!CMake Error@|')
    if line.startswith('Call Stack (most recent call first):'):
        # CMake Call Stack
        cline = cline.replace('Call Stack (most recent call first):',
                              '@{cf}@_Call Stack (most recent call first):@|')
    return fmt(cline)


def print_command_banner(cmd, cwd, color):
    if color:
        # Prepare for printing
        cmd_str = sanitize(' '.join(cmd))
        cwd_str = sanitize(cwd)
        # Print command notice
        cprint('@{bf}####')
        cprint('@{bf}#### Running command: @!"%s"@|@{bf} in @!"%s"' % (cmd_str, cwd_str))
        cprint('@{bf}####')
    else:
        print('####')
        print('#### Running command: "%s" in "%s"' % (' '.join(cmd), cwd))
        print('####')


def run_command_colorized(cmd, cwd, quiet=False, env=None):
    run_command(cmd, cwd, quiet=quiet, colorize=True, env=env)


def run_command(cmd, cwd, quiet=False, colorize=False, env=None):
    capture = (quiet or colorize)
    stdout_pipe = subprocess.PIPE if capture else None
    stderr_pipe = subprocess.STDOUT if capture else None
    try:
        proc = subprocess.Popen(
            cmd, cwd=cwd, shell=False,
            stdout=stdout_pipe, stderr=stderr_pipe, env=env
        )
    except OSError as e:
        raise OSError("Failed command '%s': %s" % (cmd, e))
    out = io.StringIO() if quiet else sys.stdout
    if capture:
        while True:
            line = proc.stdout.readline().decode('utf8', 'replace')
            line = unicode(line)
            if proc.returncode is not None or not line:
                break
            try:
                line = colorize_line(line) if colorize else line
            except Exception as e:
                import traceback
                traceback.print_exc()
                print('<yujin_make> color formatting problem: ' + str(e),
                      file=sys.stderr)
            out.write(line)
    proc.wait()
    if proc.returncode:
        if quiet:
            print(out.getvalue())
        raise subprocess.CalledProcessError(proc.returncode, ' '.join(cmd))
    return out.getvalue() if quiet else ''

blue_arrow = '@!@{bf}==>@|@!'


def _check_build_dir(name, workspace, buildspace):
    package_build_dir = os.path.join(buildspace, name)
    if not os.path.exists(package_build_dir):
        cprint(
            blue_arrow + ' Creating build directory: \'' +
            os.path.relpath(package_build_dir, workspace) + '\'@|'
        )
        os.mkdir(package_build_dir)
    return package_build_dir


def isolation_print_command(cmd, path=None):
    cprint(
        blue_arrow + " " + sanitize(cmd) + "@|" +
        (" @!@{kf}in@| '@!" + sanitize(path) + "@|'" if path else '')
    )


def get_python_path(path):
    python_path = []
    lib_path = os.path.join(path, 'lib')
    if os.path.exists(lib_path):
        items = os.listdir(lib_path)
        for item in items:
            if os.path.isdir(item) and item.startswith('python'):
                python_items = os.listdir(os.path.join(lib_path, item))
                for py_item in python_items:
                    if py_item in ['dist-packages', 'site-packages']:
                        py_path = os.path.join(lib_path, item, py_item)
                        if os.path.isdir(py_path):
                            python_path.append(py_path)
    return python_path


def build_catkin_package(
    path, package,
    workspace, buildspace, develspace, installspace,
    install, jobs, force_cmake, quiet, cmake_args, make_args,
    catkin_python_path
):
    cprint(
        "Processing @{cf}catkin@| package: '@!@{bf}" +
        package.name + "@|'"
    )

    # Make the build dir
    build_dir = _check_build_dir(package.name, workspace, buildspace)

    # Help find catkin cmake and python
    env = os.environ.copy()
    try:
        env['PYTHONPATH'] = env['PYTHONPATH'] + os.pathsep + catkin_python_path
    except KeyError:
        env['PYTHONPATH'] = catkin_python_path

    # Check for Makefile and maybe call cmake
    makefile = os.path.join(build_dir, 'Makefile')
    # check if toolchain.cmake, config.cmake exist
    toolchain_cmd = "-DCMAKE_TOOLCHAIN_FILE=%s" % os.path.join(workspace, 'toolchain.cmake') if os.path.isfile(os.path.join(workspace, 'toolchain.cmake')) else None
    config_cmd = "-C%s" % os.path.join(workspace, 'config.cmake') if os.path.isfile(os.path.join(workspace, 'config.cmake')) else None
    if not os.path.exists(makefile) or force_cmake:
        package_dir = os.path.dirname(package.filename)
        if not os.path.exists(os.path.join(package_dir, 'CMakeLists.txt')):
            export_tags = [e.tagname for e in package.exports]
            if 'metapackage' not in export_tags:
                print(colorize_line('Error: Package "%s" does not have a CMakeLists.txt file' % package.name))
                raise RuntimeError('Can not build catkin package without CMakeLists.txt file')
            # generate CMakeLists.txt for metpackages without one
            print(colorize_line('Warning: metapackage "%s" should have a CMakeLists.txt file' % package.name))
            cmake_code = configure_file(
                get_metapackage_cmake_template_path(),
                {'name': package.name, 'metapackage_arguments': 'DIRECTORY "%s"' % package_dir})
            cmakelists_txt = os.path.join(build_dir, 'CMakeLists.txt')
            with open(cmakelists_txt, 'w') as f:
                f.write(cmake_code)
            package_dir = build_dir

        # Run cmake
        cmake_cmd = [
            'cmake',
            package_dir,
        ]
        if toolchain_cmd:
            cmake_cmd.append(toolchain_cmd)
        if config_cmd:
            cmake_cmd.append(config_cmd)
        cmake_cmd.extend(cmake_args)
        isolation_print_command(' '.join(cmake_cmd))
        #if last_env is not None:
        #    cmake_cmd = [last_env] + cmake_cmd
        try:
            run_command_colorized(cmake_cmd, build_dir, quiet, env=env)
        except subprocess.CalledProcessError as e:
            # remove Makefile to force CMake invocation next time
            os.remove(makefile)
            raise
    else:
        print('Makefile exists, skipping explicit cmake invocation...')
        # Check to see if cmake needs to be run via make
        make_check_cmake_cmd = ['make', 'cmake_check_build_system']
        isolation_print_command(' '.join(make_check_cmake_cmd), build_dir)
        #if last_env is not None:
        #    make_check_cmake_cmd = [last_env] + make_check_cmake_cmd
        run_command_colorized(
            make_check_cmake_cmd, build_dir, quiet, env=env
        )

    # Run make
    make_cmd = ['make', '-j' + str(jobs), '-l' + str(jobs)]
    make_cmd.extend(make_args)
    isolation_print_command(' '.join(make_cmd), build_dir)
    #if last_env is not None:
    #    make_cmd = [last_env] + make_cmd
    run_command(make_cmd, build_dir, quiet, env=env)

    # Make install
    if install:
        make_install_cmd = ['make', 'install']
        isolation_print_command(' '.join(make_install_cmd), build_dir)
        #if last_env is not None:
        #    make_install_cmd = [last_env] + make_install_cmd
        run_command(make_install_cmd, build_dir, quiet)


def build_cmake_package(
    path, package,
    workspace, buildspace, develspace, installspace,
    install, jobs, force_cmake, quiet, cmake_args, make_args,
    catkin_cmake_path
):
    # Ros typically puts the package devel space as devel/<pkg_name>.
    # Undesirable here since we want it to do normal cmake installs
    # of everything into devel/ OR have environment chaining
    # everywhere. ugh. Changing this for now - DJS.
    develspace = os.path.abspath(os.path.join(develspace, os.pardir))
    # Notify the user that we are processing a plain cmake package
    cprint(
        "Processing @{cf}plain cmake@| package: '@!@{bf}" + package.name +
        "@|'"
    )

    # Make the build dir
    build_dir = _check_build_dir(package.name, workspace, buildspace)

    # Check for Makefile and maybe call cmake
    makefile = os.path.join(build_dir, 'Makefile')
    install_target = installspace if install else develspace
    if not os.path.exists(makefile) or force_cmake:
        # Call cmake
        cmake_cmd = [
            'cmake',
            os.path.dirname(package.filename),
            '-DCMAKE_INSTALL_PREFIX=' + install_target
        ]
        cmake_cmd.extend(cmake_args)
        isolation_print_command(' '.join(cmake_cmd))
        run_command_colorized(cmake_cmd, build_dir, quiet)
    else:
        print('Makefile exists, skipping explicit cmake invocation...')
        # Check to see if cmake needs to be run via make
        make_check_cmake_cmd = ['make', 'cmake_check_build_system']
        isolation_print_command(' '.join(make_check_cmake_cmd), build_dir)
        run_command_colorized(
            make_check_cmake_cmd, build_dir, quiet
        )

    # Run make
    make_cmd = ['make', '-j' + str(jobs), '-l' + str(jobs)]
    make_cmd.extend(make_args)
    isolation_print_command(' '.join(make_cmd), build_dir)
    run_command(make_cmd, build_dir, quiet)

    # Make install
    make_install_cmd = ['make', 'install']
    isolation_print_command(' '.join(make_install_cmd), build_dir)
    run_command(make_install_cmd, build_dir, quiet)

    # If we are installing, and a env.sh exists, don't overwrite it
#    if install and os.path.exists(os.path.join(installspace, 'env.sh')):
#        return
#    cprint(blue_arrow + " Generating an env.sh")
    # Generate env.sh for chaining to catkin packages
#    new_env_path = os.path.join(install_target, 'env.sh')
#    variables = {
#        'SETUP_DIR': install_target,
#        'SETUP_FILENAME': 'setup'
#    }
#    with open(os.path.join(new_env_path), 'w') as f:
#        f.write(configure_file(os.path.join(catkin_cmake_path, 'templates', 'env.sh.in'), variables))
#    os.chmod(new_env_path, stat.S_IXUSR | stat.S_IWUSR | stat.S_IRUSR)
#
#    # Generate setup.sh for chaining to catkin packages
#    new_setup_path = os.path.join(install_target, 'setup.sh')
#    subs = {}
#    subs['cmake_prefix_path'] = install_target + ":"
#    subs['ld_path'] = os.path.join(install_target, 'lib') + ":"
#    pythonpath = ":".join(get_python_path(install_target))
#    if pythonpath:
#        pythonpath += ":"
#    subs['pythonpath'] = pythonpath
#    subs['pkgcfg_path'] = os.path.join(install_target, 'lib', 'pkgconfig')
#    subs['pkgcfg_path'] += ":"
#    subs['path'] = os.path.join(install_target, 'bin') + ":"
#    if not os.path.exists(install_target):
#        os.mkdir(install_target)
#    with open(new_setup_path, 'w+') as file_handle:
#        file_handle.write("""\
##!/usr/bin/env sh
## generated from catkin.builder module
#
#""")
#        if last_env is not None:
#            last_setup_env = os.path.join(os.path.dirname(last_env), 'setup.sh')
#            file_handle.write('. %s\n\n' % last_setup_env)
#        file_handle.write("""\
## detect if running on Darwin platform
#UNAME=`which uname`
#UNAME=`$UNAME`
#IS_DARWIN=0
#if [ "$UNAME" = "Darwin" ]; then
#  IS_DARWIN=1
#fi
#
## Prepend to the environment
#export CMAKE_PREFIX_PATH="{cmake_prefix_path}$CMAKE_PREFIX_PATH"
#if [ $IS_DARWIN -eq 0 ]; then
#  export LD_LIBRARY_PATH="{ld_path}$LD_LIBRARY_PATH"
#else
#  export DYLD_LIBRARY_PATH="{ld_path}$DYLD_LIBRARY_PATH"
#fi
#export PATH="{path}$PATH"
#export PKG_CONFIG_PATH="{pkgcfg_path}$PKG_CONFIG_PATH"
#export PYTHONPATH="{pythonpath}$PYTHONPATH"
#
#exec "$@"
#""".format(**subs)
#        )


def build_package(
    path, package,
    workspace, buildspace, develspace, installspace,
    install, jobs, force_cmake, quiet, cmake_args, make_args,
    number=None, of=None,
    catkin_cmake_path=None,
    catkin_python_path=None
):

    cprint('@!@{gf}==>@| ', end='')
    #new_last_env = get_new_env(package, develspace, installspace, install, last_env)
    build_type = _get_build_type(package)
    if build_type == 'catkin':
        build_catkin_package(
            path, package,
            workspace, buildspace, develspace, installspace,
            install, jobs, force_cmake, quiet, cmake_args, make_args,
            catkin_python_path
        )
        #if not os.path.exists(new_last_env):
        #    raise RuntimeError(
        #        "No env.sh file generated at: '" + new_last_env +
        #        "'\n  This sometimes occurs when a non-catkin package is "
        #        "interpreted as a catkin package.\n  This can also occur "
        #        "when the cmake cache is stale, try --force-cmake."
        #    )
    elif build_type == 'cmake':
        build_cmake_package(
            path, package,
            workspace, buildspace, develspace, installspace,
            install, jobs, force_cmake, quiet, cmake_args, make_args,
            catkin_cmake_path
        )
    else:
        raise RuntimeError('Can not build package with unknown build_type')
    if number is not None and of is not None:
        msg = ' [@{gf}@!' + str(number) + '@| of @!@{gf}' + str(of) + '@|]'
    else:
        msg = ''
    cprint('@{gf}<==@| Finished processing package' + msg + ': \'@{bf}@!' +
           package.name + '@|\'')


def get_new_env(package, develspace, installspace, install, last_env):
    new_env = None
    build_type = _get_build_type(package)
    if build_type in ['catkin', 'cmake']:
        new_env = os.path.join(
            installspace if install else develspace,
            'env.sh'
        )
    return new_env


def _get_build_type(package):
    build_type = 'catkin'
    if 'build_type' in [e.tagname for e in package.exports]:
        build_type = [e.content for e in package.exports if e.tagname == 'build_type'][0]
    return build_type


def cmake_input_changed(packages, build_path, install=None, cmake_args=None, filename='catkin_make'):
    # get current input
    package_paths = os.pathsep.join(sorted(packages.keys()))
    cmake_args = ' '.join(cmake_args) if cmake_args else ''

    # file to store current input
    changed = False
    install_toggled = False
    input_filename = os.path.join(build_path, '%s.cache' % filename)
    if not os.path.exists(input_filename):
        changed = True
    else:
        # compare with previously stored input
        with open(input_filename, 'r') as f:
            previous_package_paths = f.readline().rstrip()
            previous_cmake_args = f.readline().rstrip()
            previous_install = f.readline().rstrip() == str(True)
        if package_paths != previous_package_paths:
            changed = True
        if cmake_args != previous_cmake_args:
            changed = True
        if install is not None and install != previous_install:
            install_toggled = True

    # store current input for next invocation
    with open(input_filename, 'w') as f:
        f.write('%s\n%s\n%s' % (package_paths, cmake_args, install))
    return changed, install_toggled
