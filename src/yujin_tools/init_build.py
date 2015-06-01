##############################################################################
# Imports
##############################################################################

import os.path

import stat  # file permissions
import argparse
from argparse import RawTextHelpFormatter
import shutil

##############################################################################
# Local imports
##############################################################################

import console
import common
import settings

##############################################################################
# Methods
##############################################################################


def help_string():
    overview = 'This is a convenience script for auto-generating a catkin parallel build directory.\n\n'
    instructions = " \
 'yujin_init_build .' prepares conventional ros build directories in ./ linked to sources in ./src \n \
 'yujin_init_build .' prepares conventional ros build directories in ./ linked to sources in ./src \n \
 'yujin_init_build --release release' prepares a release directory in ./release linked to sources in ./src \n \
 'yujin_init_build debug ~/ecl/src' prepares a build directory in ./debug linked to sources in ~/ecl/src \n \
 'yujin_init_build --no-default-underlay --toolchain=arm-pc-linux-gnueabi arm' prepares a build directory in ./arm with the specified toolchain module \n \
 'yujin_init_build --underlays=~/cslam/src/native;~/ecl/src/native .' prepares a build directory in ./arm with the specified toolchain module \n \
 \n \
 Underlays automatically add /opt/ros/`yujin_tools_settings --get-default-track` unless '--no-default-underlay' is specified (in which case you should\n \
 ensure that the catkin sources are in your workspace or one of your underlays).\n \
"
    return overview + instructions


def parse_arguments():
    parser = argparse.ArgumentParser(description=help_string(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('dir', nargs='?', default=".", help='directory to use for the parallel development space [./]')
    parser.add_argument('sources', nargs='?', default="src", help='directory where the sources reside [./src]')
    parser.add_argument('-r', '--release', action='store_true', help='build in Release mode instead of RelWithDebInfo [false]')
    parser.add_argument('-i', '--install', action='store', default='/not_set_directory', help='installation location [workspace/install]')
    parser.add_argument('-d', '--doc', action='store', default='/not_set_directory', help='document location [workspace/doc]')
    #  even though we don't set a default value here, it later gets set as the default underlay if not present and --no-default-underlay is not true
    parser.add_argument('-u', '--underlays', action='store', default='', help='semi-colon list of catkin workspaces to utilise, priority given from front to back')
    default_underlay_group = parser.add_mutually_exclusive_group()
    default_underlay_group.add_argument('-du', '--default-underlay', choices=settings.VALID_TRACKS, action='store', default=None, help='default the underlays to this track if catkin is not found [`yujin_tools_settings --get-default-track`]')
    default_underlay_group.add_argument('--track', choices=settings.VALID_TRACKS, dest='default_underlay', action='store', default=None, help='convenience equivalent for the --default-underlay option')
    default_underlay_group.add_argument('-n', '--no-default-underlay', action='store_true', help='do not automatically underlay with the default track setting [false]')
    parser.add_argument('-t', '--toolchain', action='store', default='', help='toolchain cmake module to load []')
    parser.add_argument('-p', '--platform', action='store', default='default', help='platform cmake cache module to load [default]')
    parser.add_argument('-c', '--clean', action='store_true', help='cleans the current or specified build directory [false]')
    parser.add_argument('--list-toolchains', action='store_true', help='list all currently available toolchain modules [false]')
    parser.add_argument('--list-platforms', action='store_true', help='list all currently available platform modules [false]')
    args = parser.parse_args()
    return args


def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, unused_fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def read_template(tmplf):
    f = open(tmplf, 'r')
    try:
        t = f.read()
    finally:
        f.close()
    return t


def fill_in_template(template, name, cwd):
    return template % locals()


def instantiate_template(filename, name, cwd):
    template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'init_build')
    tmpl = read_template(os.path.join(template_dir, filename))
    contents = fill_in_template(tmpl, name, cwd)
    try:
        f = open(os.path.join(cwd, filename), 'w')
        f.write(contents.encode('utf-8'))
    finally:
        os.fchmod(f.fileno(), stat.S_IRWXU | stat.S_IRWXG)
        f.close()


def fill_in_config_cmake(template, config_build_type, config_devel, config_install_prefix, config_doc_prefix, config_underlays, config_override_file):
    return template % locals()


def instantiate_config_cmake(platform_content, build_path, config_build_type, config_install_prefix, config_doc_prefix, config_underlays):
    '''
      Copy the cache configuration template to the build path.

      @param platform_content : content to prepend to the default configuration file
      @param build_path : location of the build directory to save the config.cmake file.
    '''
    template_dir = os.path.join(os.path.dirname(__file__), 'cmake')
    template = read_template(os.path.join(template_dir, "config.cmake"))
    config_devel = os.path.join(build_path, 'devel')
    contents = fill_in_config_cmake(template, config_build_type, config_devel, config_install_prefix, config_doc_prefix, config_underlays, common.override_filename())
    config_cmake_file = os.path.join(build_path, "config.cmake")
    try:
        f = open(config_cmake_file, 'w')
        f.write(platform_content.encode('utf-8'))
        f.write(contents.encode('utf-8'))
    finally:
        f.close()


def print_build_details(build_dir, source_dir, install_prefix, doc_prefix, build_type, underlays, name, toolchain, platform):
    console.pretty_println("\n************************** Parallel Buildspace Details ***************************", console.bold)
    console.pretty_print(" -- Build directory : ", console.cyan)
    console.pretty_println(build_dir, console.yellow)
    console.pretty_print(" -- Source directory: ", console.cyan)
    console.pretty_println(source_dir, console.yellow)
    console.pretty_print(" -- Install prefix  : ", console.cyan)
    console.pretty_println(install_prefix, console.yellow)
    console.pretty_print(" -- Document prefix : ", console.cyan)
    console.pretty_println(doc_prefix, console.yellow)
    console.pretty_print(" -- Build Type      : ", console.cyan)
    console.pretty_println(build_type, console.yellow)
    underlays_list = underlays.split(';')
    console.pretty_print(" -- Underlays       : ", console.cyan)
    if len(underlays_list) == 0:
        console.pretty_println("-", console.yellow)
    else:
        underlay = underlays_list.pop(0)
        console.pretty_println(underlay, console.yellow)
        for underlay in underlays_list:
            console.pretty_print("                    : ", console.cyan)
            console.pretty_println(underlay, console.yellow)
    console.pretty_print(" -- Eclipse Name    : ", console.cyan)
    console.pretty_println(name, console.yellow)
    if not toolchain == "":
        console.pretty_print(" -- Toolchain       : ", console.cyan)
        console.pretty_println(toolchain, console.yellow)
    if not platform == "":
        console.pretty_print(" -- Platform        : ", console.cyan)
        console.pretty_println(platform, console.yellow)
    console.pretty_println("**********************************************************************************\n", console.bold)


def write_yujin_init_build_configuration(build_source_dir, source_dir):
    try:
        f = open(os.path.join(build_source_dir, '.yujin_init_build'), 'w')
        rel_path = os.path.relpath(source_dir, build_source_dir)
        f.write(rel_path.encode('utf-8'))
    finally:
        f.close()


def get_toolchains_or_platforms(base_path):
    '''
      Does a look up in the path for either toolchain or platform files.
      @param base_path : start of the search (ends in either toolchains or platforms).
    '''
    d = {}
    for (dirpath, unused_dirname, filenames) in os.walk(base_path):
        if dirpath != base_path:  # skip the root, only find files in subfolders
            family = os.path.basename(dirpath)
            d[family] = []
            for filename in filenames:
                d[family].append(os.path.splitext(filename)[0])  # leave off the .cmake extension
    return d


def list_toolchains():
    console.pretty_println("\n******************************** Toolchain List **********************************", console.bold)
    toolchains = get_toolchains_or_platforms(os.path.join(os.path.dirname(__file__), 'toolchains'))
    console.pretty_println("Official:", console.bold)
    for family in toolchains:
        for platform in toolchains[family]:
            console.pretty_print(" -- %s/" % family, console.cyan)
            console.pretty_println("%s" % platform, console.yellow)
    console.pretty_println("Custom:", console.bold)
    toolchains = get_toolchains_or_platforms(os.path.join(settings.yujin_tools_home(), 'toolchains'))
    if toolchains:
        for family in toolchains:
            for platform in toolchains[family]:
                console.pretty_print(" -- %s/" % family, console.cyan)
                console.pretty_println("%s" % platform, console.yellow)
    else:
        console.pretty_println(" -- ", console.cyan)
    console.pretty_println("**********************************************************************************\n", console.bold)


def list_platforms():
    console.pretty_println("\n********************************* Platform List **********************************", console.bold)
    platforms = get_toolchains_or_platforms(os.path.join(os.path.dirname(__file__), 'platforms'))
    console.pretty_println("Official:", console.bold)
    for family in platforms:
        for platform in platforms[family]:
            console.pretty_print(" -- %s/" % family, console.cyan)
            console.pretty_println("%s" % platform, console.yellow)
    console.pretty_println("Custom:", console.bold)
    platforms = get_toolchains_or_platforms(os.path.join(settings.yujin_tools_home(), 'platforms'))
    if platforms:
        for family in platforms:
            for platform in platforms[family]:
                console.pretty_print(" -- %s/" % family, console.cyan)
                console.pretty_println("%s" % platform, console.yellow)
    else:
        console.pretty_println(" -- ", console.cyan)
    console.pretty_println("**********************************************************************************\n", console.bold)


def init_configured_build(default_underlay, build_dir_="./", source_dir_="./src", underlays_="/opt/ros/groovy", install_prefix_="./install", doc_prefix_="./doc", release_=False, toolchain_="", platform_=""):
    '''
      This one is used with pre-configured parameters. Note that
      init_build generates parameters parsed from the command line and then
      calls this function.
    '''
    # Help us build the name for the eclipse workspace...usually we call in the workspace itself.
    workspace_dir = os.getcwd()

    ##########################
    # Build directory
    ##########################
    if os.path.isabs(build_dir_):
        build_dir = build_dir_
    else:
        if build_dir_ == "." or build_dir_ == "./":
            build_dir = os.getcwd()
        else:
            build_dir = os.path.join(os.getcwd(), build_dir_)
    if not os.path.isfile(os.path.join(build_dir, "Makefile")):
        if not os.path.isdir(build_dir):  # remember ./ is a valid build dir, even if it's not populated yet
            os.mkdir(build_dir)
    else:
        raise RuntimeError("This build directory is already initialised")

    ##########################
    # Source directory
    ##########################
    source_dir = os.path.abspath(source_dir_)
    build_source_dir = os.path.join(build_dir, 'src')
    if not os.path.isdir(source_dir):
        raise RuntimeError("Specified source space does not exist [" + source_dir + "]")
    if not os.path.isfile(os.path.join(source_dir, ".rosinstall")):
        raise RuntimeError("Could not find a valid source folder (must contain a .rosinstall file therein)'")
    if os.path.exists(build_source_dir):
        if not source_dir == build_source_dir:
            raise RuntimeError("The build directory already has a ./src directory which doesn't match the desired source directory [%s]" % source_dir)
    else:
        os.mkdir(build_source_dir)
        source_subdirectories = os.walk(source_dir).next()[1]
        for d in source_subdirectories:
            common.create_symlink(os.path.join(source_dir, d), os.path.join(build_source_dir, d))
    write_yujin_init_build_configuration(build_source_dir, source_dir)

    ##########################
    # Underlays
    ##########################
    try:
        env_underlays = os.environ['CMAKE_PREFIX_PATH']
    except KeyError:
        env_underlays = ""
    underlays_list = [underlay for underlay in underlays_.split(';') if underlay]
    env_underlays_list = [underlay for underlay in env_underlays.split(':') if underlay]
    for underlay in env_underlays_list:
        if underlay not in underlays_list:
            underlays_list.append(underlay)

    ##########################
    # Locate Catkin
    ##########################
    catkin_toplevel = None
    if os.path.isfile(os.path.join(source_dir, 'catkin', 'cmake', 'toplevel.cmake')):
        catkin_toplevel = os.path.join(source_dir, 'catkin', 'cmake', 'toplevel.cmake')
    else:
        catkin_toplevel, unused_catkin_python_path, unused_catkin_cmake_path = common.find_catkin(build_dir, underlays_list)

    ##########################
    # Add toplevel if exists
    ##########################
    if not catkin_toplevel:
        # Add the default underlay
        if default_underlay is not None and os.path.isfile(os.path.join("/opt/ros/%s" % default_underlay, 'share', 'catkin', 'cmake', 'toplevel.cmake')):
            catkin_toplevel = os.path.join("/opt/ros/%s" % default_underlay, 'share', 'catkin', 'cmake', 'toplevel.cmake')
            unused_catkin_python_path = os.path.join("/opt/ros/%s" % default_underlay, 'lib', 'python2.7', 'dist-packages')
            console.pretty_println("No catkin found, adding the default underlay (use yujin_tools_settings to change) [/opt/ros/%s]" % default_underlay, console.cyan)
            underlays_list.append("/opt/ros/%s" % default_underlay)
        else:
            raise RuntimeError("Could not find an underlying catkin installation.")
    common.create_symlink(catkin_toplevel, os.path.join(build_source_dir, "CMakeLists.txt"))
    underlays = ';'.join(underlays_list)

    ##########################
    # Other Args
    ##########################
    if install_prefix_ == "/not_set_directory":
        install_prefix = os.path.join(build_dir, "install")
    else:
        install_prefix = install_prefix_

    if doc_prefix_ == "/not_set_directory":
        doc_prefix = os.path.join(build_dir, "doc")
    else:
        doc_prefix = doc_prefix_

    if release_:
        build_type = "Release"
    else:
        build_type = "RelWithDebInfo"
    name = os.path.basename(workspace_dir) + "_" + os.path.basename(build_dir)

    print_build_details(build_dir, source_dir, install_prefix, doc_prefix, build_type, underlays, name, toolchain_, platform_)
    os.chdir(build_dir)

    ##########################
    # Toolchain
    ##########################
    if not toolchain_ == "":
        toolchains_dir = os.path.join(os.path.dirname(__file__), 'toolchains')
        custom_toolchains_dir = os.path.join(settings.yujin_tools_home(), 'toolchains')
        tmp_list = toolchain_.split('/')
        if len(tmp_list) != 2:
            raise RuntimeError("Toolchain specification invalid, must be <family>/<tuple> [%s]" % toolchain_)
        family = tmp_list[0]
        toolchain_tuple = tmp_list[1]
        toolchains = get_toolchains_or_platforms(toolchains_dir)
        custom_toolchains = get_toolchains_or_platforms(custom_toolchains_dir)
        if not family in toolchains and not family in custom_toolchains:
            raise RuntimeError("No toolchains available for family %s" % family)
        if family in custom_toolchains and toolchain_tuple in custom_toolchains[family]:
            toolchain_file = os.path.join(custom_toolchains_dir, family, toolchain_tuple + ".cmake")
        elif family in toolchains and toolchain_tuple in toolchains[family]:
            toolchain_file = os.path.join(toolchains_dir, family, toolchain_tuple + ".cmake")
        else:
            raise RuntimeError("Platform %s for family %s not available." % (family, toolchain_tuple))
        if os.path.isfile(toolchain_file):
            shutil.copy(toolchain_file, os.path.join(build_dir, "toolchain.cmake"))
        else:
            raise RuntimeError("Toolchain module not available [%s]" % toolchain_file)

    ##########################
    # Platform
    ##########################
    platform_content = ""
    platforms_dir = os.path.join(os.path.dirname(__file__), 'platforms')
    custom_platforms_dir = os.path.join(settings.yujin_tools_home(), 'platforms')
    if not platform_ == "default":
        tmp_list = platform_.split('/')
        if len(tmp_list) != 2:
            raise RuntimeError("Platform specification invalid, must be <family>/<platform type> [%s]" % platform_)
        family = tmp_list[0]
        platform = tmp_list[1]
        platforms = get_toolchains_or_platforms(platforms_dir)
        custom_platforms = get_toolchains_or_platforms(custom_platforms_dir)
        if not family in platforms and not family in custom_platforms:
            raise RuntimeError("No platforms available for family %s" % family)
        if family in custom_platforms and platform in custom_platforms[family]:
            platform_file = os.path.join(custom_platforms_dir, family, platform + ".cmake")
        elif family in platforms and platform in platforms[family]:
            platform_file = os.path.join(platforms_dir, family, platform + ".cmake")
        else:
            raise RuntimeError("Platform %s for family %s not available." % (family, platform))
    else:
        platform_file = os.path.join(platforms_dir, 'default.cmake')

    if os.path.isfile(platform_file):
        f = open(platform_file, 'r')
        try:
            platform_content = f.read()
        finally:
            f.close()
    else:
        raise RuntimeError("Platform configuration not available [%s]" % platform_)

    ##########################
    # Cache
    ##########################
    instantiate_config_cmake(platform_content, build_dir, build_type, install_prefix, doc_prefix, underlays)

    ##########################
    # Templates
    ##########################
    instantiate_template('.bashrc', name, build_dir)
    instantiate_template('konsole', name, build_dir)
    instantiate_template('gnome-terminal', name, build_dir)
    instantiate_template('eclipse', name, build_dir)
    instantiate_template('android-studio', name, build_dir)


def clean(dir_to_be_cleaned, dir_sources):
    if common.is_same_dir(dir_to_be_cleaned, os.getcwd()):
        if not os.path.isfile(os.path.join(dir_to_be_cleaned, 'config.cmake')):
            console.logerror("Could not clean the current directory [build artifacts do not exist]")
            return
        console.pretty_print("\nCleaning current directory of yujin_init_build artifacts : ", console.cyan)
        for f in [os.path.join(dir_to_be_cleaned, x) for x in ['config.cmake', 'eclipse', 'gnome-terminal', 'konsole', 'toolchain.cmake', '.bashrc', 'android-studio']]:
            if os.path.isfile(f):
                os.remove(f)
        for f in [os.path.join(dir_to_be_cleaned, dir_sources, x) for x in ['CMakeLists.txt', '.yujin_init_build']]:
            if os.path.isfile(f):
                os.remove(f)
        for d in [os.path.join(dir_to_be_cleaned, x) for x in ['build', 'devel']]:
            if os.path.isdir(d):
                shutil.rmtree(d)
        console.pretty_println('done.\n', console.yellow)
    else:
        if os.path.isdir(os.path.abspath(dir_to_be_cleaned)):
            console.pretty_print("Cleaning build directory : ", console.cyan)
            console.pretty_println(dir_to_be_cleaned, console.yellow)
            shutil.rmtree(os.path.abspath(dir_to_be_cleaned))
        else:
            console.logerror("Could not clean %s [does not exist]" % dir_to_be_cleaned)


def init_build():
    args = parse_arguments()

    ##########################
    # Default underlays
    ##########################
    if args.no_default_underlay:
        args.default_underlay = None
    elif not args.default_underlay:
        args.default_underlay = settings.get_default_track()

    ##########################
    # Toolchains and Platform
    ##########################
    if args.list_toolchains:
        list_toolchains()
        return
    if args.list_platforms:
        list_platforms()
        return
    if args.clean:
        clean(args.dir, args.sources)
        return
    init_configured_build(args.default_underlay, args.dir, args.sources, args.underlays, args.install, args.doc, args.release, args.toolchain, args.platform)
