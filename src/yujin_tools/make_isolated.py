##############################################################################
# Imports
##############################################################################

import os.path
import sys
import stat  # file permissions
import argparse
import subprocess
import copy
import shutil
try:
    from catkin_pkg.packages import find_packages
    from catkin_pkg.topological_order import topological_order_packages
    from catkin_pkg.cmake import configure_file
    #, get_metapackage_cmake_template_path
except ImportError as e:
    sys.exit(
        'ImportError: "from catkin_pkg.topological_order import '
        'topological_order" failed: %s\nMake sure that you have installed '
        '"catkin_pkg", it is up to date and on the PYTHONPATH.' % e
    )

##############################################################################
# Local imports
##############################################################################

import console
import common
import config_cache
import make

import catkin_make.terminal_color as terminal_color
#from catkin_make.terminal_color import fmt
import catkin_make.builder as builder  # extract_cmake_and_make_arguments, cmake_input_changed

##############################################################################
# Methods
##############################################################################


def _parse_args(args=sys.argv[1:]):
    args, cmake_args, make_args = builder.extract_cmake_and_make_arguments(args)

    parser = argparse.ArgumentParser(
        description='Builds each catkin (and non-catkin) package from '
                    'a given workspace in isolation, but still in '
                    'topological order.'
    )
    parser.add_argument('--merge', action='store_true', default=False, help='Build each catkin package into a common devel space.')
    parser.add_argument('-j', '--jobs', type=int, metavar='JOBS', nargs='?', default=None, help='Specifies the number of jobs (commands) to run simultaneously. Defaults to the environment variable ROS_PARALLEL_JOBS and falls back to the number of CPU cores.')
    parser.add_argument('-i', '--install', action='store_true', default=False, help='Run install step after making [false]')
    parser.add_argument('--strip', action='store_true', help='Strips binaries, only valid with --install')
    parser.add_argument('--force-cmake', action='store_true', default=False, help='Invoke "cmake" even if it has been executed before [false]')
    parser.add_argument('--no-color', action='store_true', help='Disables colored ouput')
    parser.add_argument('--target', default=None, help='Build against a particular target only')
    parser.add_argument('--pkg', nargs='+', metavar='PKGNAME', dest='packages', help='Invoke "make" on specific packages (only after initial invocation)')
    parser.add_argument('-s', '--suffixes', action='store_true', default=False, help='Add _isolated to build/install paths.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='Suppresses the cmake and make output until an error occurs.')
    parser.add_argument('-p', '--pre-clean', action='store_true', help='Clean build temporaries before making [false]')
    parser.add_argument('--cmake-args', dest='cmake_args', nargs='*', type=str,
        help='Arbitrary arguments which are passes to CMake. It must be passed after other arguments since it collects all following options.')
    parser.add_argument('--make-args', dest='make_args', nargs='*', type=str,
        help='Arbitrary arguments which are passes to make. It must be passed after other arguments since it collects all following options. This is only necessary in combination with --cmake-args since else all unknown arguments are passed to make anyway.')

    options, unknown_args = parser.parse_known_args(args)
    if not options.jobs and not [a for a in args if a == '-j' or a == '--jobs']:
        options.jobs = common.good_number_of_jobs()
    options.cmake_args = cmake_args
    options.make_args = unknown_args + make_args
    if options.strip:
      options.target = "install/strip"
    return options

def make_isolated_main():
    args = _parse_args()

    if args.no_color:
        terminal_color.disable_ANSI_colors()

    (base_path, build_path, devel_path, source_path) = common.get_default_paths(isolated=args.suffixes)
    unused_catkin_toplevel, catkin_python_path, unused_catkin_cmake_path = common.find_catkin(base_path)
    install_path = config_cache.get_install_prefix_from_config_cmake(isolated=args.suffixes)

    sys.path.insert(0, catkin_python_path)

    from catkin.builder import build_workspace_isolated

    # Clear out previous temporaries if requested
    if args.pre_clean:
        console.pretty_print("Pre-cleaning before building.", console.cyan)
        shutil.rmtree(devel_path, ignore_errors=True)
        shutil.rmtree(build_path, ignore_errors=True)
        shutil.rmtree(install_path, ignore_errors=True)

    if not os.path.exists(build_path):
        os.mkdir(build_path)

    # Validate package argument
    packages = find_packages(source_path, exclude_subspaces=True)
    packages_by_name = {p.name: path for path, p in packages.iteritems()}
    if args.packages:
        for package in args.packages:
            if package not in packages_by_name:
                raise RuntimeError('Package %s not found in the workspace' % package)

    make.validate_build_space(base_path)  # raises a RuntimeError if there is a problem
    make.check_and_update_source_repo_paths(source_path)
    build_workspace_isolated(
        workspace=base_path,
        sourcespace=source_path,
        buildspace=build_path,
        develspace=devel_path,
        installspace=install_path,
        merge=args.merge,
        install=args.install,
        force_cmake=args.force_cmake,
        build_packages=args.packages,
        quiet=args.quiet,
        cmake_args=args.cmake_args,
        make_args=args.make_args
    )
    # this is a really fugly way of building a specific target after all else has been built
    # (and rebuilt), usually this is enough as the check of already built packages is quick
    if args.target:
        env = os.environ.copy()
        cmd = ['make', args.target]
        make_paths = []
        if args.packages:
            for package in args.packages:
                # It's an isolated build, so packages are listed under the build path as a flat list (not fully traceable dirs like in catkin_make)
                # make_path = os.path.join(make_path, packages_by_name[package])
                make_paths.append(os.path.join(build_path, package))
        else:
            for (unused_path, package) in topological_order_packages(packages):
	        # 3rd party builds put make targets under an install directory
	        # catkin package builds put make targets under the package name
	        # why? no bloody idea, but just detect what is what here
	        third_party_build_path = os.path.join(build_path, package.name, 'install')
	        catkin_build_path = os.path.join(build_path, package.name)
	        package_build_path = third_party_build_path if os.path.exists(third_party_build_path) else catkin_build_path
                make_paths.append(package_build_path)
        for make_path in make_paths:
            builder.print_command_banner(cmd, make_path, color=not args.no_color)
            if args.no_color:
                builder.run_command(cmd, make_path, env=env)
            else:
                builder.run_command_colorized(cmd, make_path, env=env)


#def dbuild_workspace_isolated(
#    workspace='.',
#    sourcespace=None,
#    buildspace=None,
#    develspace=None,
#    installspace=None,
#    merge=False,
#    install=False,
#    jobs=None,
#    force_cmake=False,
#    build_packages=None,
#    quiet=False,
#    cmake_args=[],
#    make_args=[],
#    catkin_cmake_path=None,
#    catkin_python_path=None
#):
#    '''
#    Runs ``cmake``, ``make`` and optionally ``make install`` for all
#    catkin packages in sourcespace_dir.  It creates several folders
#    in the current working directory. For non-catkin packages it runs
#    ``cmake``, ``make`` and ``make install`` for each, installing it to
#    the devel space or install space if the ``install`` option is specified.
#
#    :param workspace: path to the current workspace, ``str``
#    :param sourcespace: workspace folder containing catkin packages, ``str``
#    :param buildspace: path to build space location, ``str``
#    :param develspace: path to devel space location, ``str``
#    :param installspace: path to install space (CMAKE_INSTALL_PREFIX), ``str``
#    :param merge: if True, build each catkin package into the same
#        devel space. does not work with non-catkin packages, ``bool``
#    :param install: if True, install all packages to the install space,
#        ``bool``
#    :param jobs: number of parallel build jobs to run (make -jN -lN), ``int``
#    :param force_cmake: (optional), if True calls cmake explicitly for each
#        package, ``bool``
#    :param colorize: if True, colorize cmake output and other messages,
#        ``bool``
#    :param build_packages: specific packages to build (all parent packages
#        in the topological order must have been built before), ``str``
#    :param quiet: if True, hides some build output, ``bool``
#    :param cmake_args: additional arguments for cmake, ``[str]``
#    :param make_args: additional arguments for make, ``[str]``
#    '''
#    # Should actually have alot of argument checks here, rather than
#    # before feeding the function (makes for safe functions)
#
#    console.pretty_print("Base Path: ", console.cyan)
#    console.pretty_println("%s" % workspace, console.yellow)
#    console.pretty_print("Build Path: ", console.cyan)
#    console.pretty_println("%s" % buildspace, console.yellow)
#    console.pretty_print("Source Path: ", console.cyan)
#    console.pretty_println("%s" % sourcespace, console.yellow)
#    console.pretty_print("Devel Path: ", console.cyan)
#    console.pretty_println("%s" % develspace, console.yellow)
#    console.pretty_print("Install Path: ", console.cyan)
#    console.pretty_println("%s" % installspace, console.yellow)
#    console.pretty_print("Catkin CMake Path: ", console.cyan)
#    console.pretty_println("%s" % catkin_cmake_path, console.yellow)
#    console.pretty_print("Catkin Python Path: ", console.cyan)
#    console.pretty_println("%s" % catkin_python_path, console.yellow)
#    # Find packages
#    packages = find_packages(sourcespace, exclude_subspaces=True)
#    if not packages:
#        raise RuntimeError("No packages found in source space: %s" % sourcespace)
#
#    # verify that specified package exists in workspace
#    if build_packages:
#        packages_by_name = {p.name: path for path, p in packages.iteritems()}
#        unknown_packages = [p for p in build_packages if p not in packages_by_name]
#        if unknown_packages:
#            raise RuntimeError('Packages not found in the workspace: %s' % ', '.join(unknown_packages))
#
#    # Report topological ordering
#    ordered_packages = topological_order_packages(packages)
#    unknown_build_types = []
#    msg = []
#    msg.append('@{pf}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~' + ('~' * len(str(len(ordered_packages)))))
#    msg.append('@{pf}~~@|  traversing %d packages in topological order:' % len(ordered_packages))
#    for path, package in ordered_packages:
#        export_tags = [e.tagname for e in package.exports]
#        if 'build_type' in export_tags:
#            build_type_tag = [e.content for e in package.exports if e.tagname == 'build_type'][0]
#        else:
#            build_type_tag = 'catkin'
#        if build_type_tag == 'catkin':
#            msg.append('@{pf}~~@|  - @!@{bf}' + package.name + '@|')
#        elif build_type_tag == 'cmake':
#            msg.append(
#                '@{pf}~~@|  - @!@{bf}' + package.name + '@|' +
#                ' (@!@{cf}plain cmake@|)'
#            )
#        else:
#            msg.append(
#                '@{pf}~~@|  - @!@{bf}' + package.name + '@|' +
#                ' (@{rf}unknown@|)'
#            )
#            unknown_build_types.append(package)
#    msg.append('@{pf}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~' + ('~' * len(str(len(ordered_packages)))))
#    for index in range(len(msg)):
#        msg[index] = fmt(msg[index])
#    print('\n'.join(msg))
#
#    # Error if there are packages with unknown build_types
#    if unknown_build_types:
#        raise RuntimeError('Can not build workspace with packages of unknown build_type.')
#
#    # Check to see if the workspace has changed
#    if not force_cmake:
#        force_cmake, install_toggled = builder.cmake_input_changed(
#            packages,
#            buildspace,
#            install=install,
#            cmake_args=cmake_args,
#            filename='catkin_make_isolated'
#        )
#        if force_cmake:
#            print('The packages or cmake arguments have changed, forcing cmake invocation')
#        elif install_toggled:
#            print('The install argument has been toggled, forcing cmake invocation on plain cmake package')
#
#    # Build packages
#    original_develspace = copy.deepcopy(develspace)
#    for index, path_package in enumerate(ordered_packages):
#        path, package = path_package
#        if not merge:
#            develspace = os.path.join(original_develspace, package.name)
#        if not build_packages or package.name in build_packages:
#            try:
#                export_tags = [e.tagname for e in package.exports]
#                is_cmake_package = 'cmake' in [e.content for e in package.exports if e.tagname == 'build_type']
#                builder.build_package(
#                    path, package,
#                    workspace, buildspace, develspace, installspace,
#                    install, jobs, force_cmake or (install_toggled and is_cmake_package),
#                    quiet, cmake_args, make_args,
#                    number=index + 1, of=len(ordered_packages),
#                    catkin_cmake_path=catkin_cmake_path,
#                    catkin_python_path=catkin_python_path
#                )
#            except Exception as e:
#                import traceback
#                traceback.print_exc()
#                builder.cprint(
#                    '@{rf}@!<==@| ' +
#                    'Failed to process package \'@!@{bf}' +
#                    package.name + '@|\': \n  ' +
#                    ('KeyboardInterrupt' if isinstance(e, KeyboardInterrupt)
#                        else str(e))
#                )
#                if isinstance(e, subprocess.CalledProcessError):
#                    cmd = ' '.join(e.cmd) if isinstance(e.cmd, list) else e.cmd
#                    print(fmt("\n@{rf}Reproduce this error by running:"))
#                    print(fmt("@{gf}@!==> @|") + cmd + "\n")
#                sys.exit('Command failed, exiting.')
#        else:
#            builder.cprint("Skipping package: '@!@{bf}" + package.name + "@|'")
#
#    # Provide a top level devel space environment setup script
#    if not merge and not build_packages:
#        # generate env.sh and setup.sh which relay to last devel space
#        generated_env = os.path.join(original_develspace, 'env.sh')
#        with open(generated_env, 'w') as f:
#            f.write("""\
##!/usr/bin/env sh
## generated from catkin.builder module
#
#{0} "$@"
#""".format(os.path.join(develspace, 'env.sh')))
#        os.chmod(generated_env, stat.S_IXUSR | stat.S_IWUSR | stat.S_IRUSR)
#        with open(os.path.join(original_develspace, 'setup.sh'), 'w') as f:
#            f.write("""\
##!/usr/bin/env sh
## generated from catkin.builder module
#
#. "{0}/setup.sh"
#""".format(develspace))
#        # generate setup.bash and setup.zsh for convenience
#        variables = {'SETUP_DIR': original_develspace}
#        with open(os.path.join(original_develspace, 'setup.bash'), 'w') as f:
#            f.write(configure_file(os.path.join(catkin_cmake_path, 'templates', 'setup.bash.in'), variables))
#        with open(os.path.join(original_develspace, 'setup.zsh'), 'w') as f:
#            f.write(configure_file(os.path.join(catkin_cmake_path, 'templates', 'setup.zsh.in'), variables))
