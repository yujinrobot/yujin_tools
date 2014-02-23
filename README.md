Yujin Tools
=========

Utilies for yujin development. These are system tools (i.e. not deployed within a 
ros environment).


## Tools

* **Configuration**
 * `yujin_tools_settings` : configure the rosdistro the yujin tools should work with.
* **Compiling**
 * `yujin_init_workspace` : easy rosinstaller, drop in a listed rosinstall from the yujin tools rosinstall database.
 * `yujin_init_build` : configure a build dir and populate with environment startup scripts (esp. useful for parallel builds)
 * `yujin_make` : catkin_make on drugs
* **Rocon**
 * `avahi-browse-concerts`
 * `avahi-browse-multimaster`
 * `masteruri` : quickly switch between ROS_MASTER_URI's (e.g. `. masteruri 2` -> 11312)
* **General Purpose**
 * `yujin_list_git_branches` : list branches of all rosinstalls in a ros source workspace.

## Usage

### Installation

    > sudo apt-get install python-pip
    > sudo pip install --upgrade yujin_tools

### Usage

**yujin_tools_settings**

This allows you to configure the rosdistro yujin_make and co. should work with. Calling with --help
should be sufficient to grasp this tool.

**yujin_init_workspace**, **yujin_init_buld**, **yujin_make**

* [Yujin Init Tools](https://github.com/yujinrobot/yujin_tools/wiki/yujin-init)

**masteruri**

Allows checking and switching of `ROS_MASTER_URI`'s on localhost.

    # To check the current value:
    > masteruri
    http://localhost:11311
    # To switch
    > . masteruri 2
    > masteruri
    http://localhost:11312

**yujin_list_git_branches**

Use in the src directory of a catkin_make/yujin_make installed source workspace populated with git
clones. This will list the branches in each and highlight the currently used branch.

## Developing & Packaging

For the yujin guys:

    > git clone https://github.com/yujinrobot/yujin_tools.git
    > cd yujin_tools

* make some changes
* bump the version in `src/yujin_tools/__init__.py
* add a note to the `Changelog`

Finally, upload

    > make build
    > make upload

See Daniel if you need permissions for uploading.
