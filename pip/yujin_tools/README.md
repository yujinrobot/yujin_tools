Yujin Tools
=========

Utilies for yujin development. These are system tools (i.e. not deployed within a 
ros environment).

Template style wizard shortcuts for creating ros packages, stacks.

## Tools

* cfind 
* yujin_init_workspace
* roscreate-shortcuts

## Usage

### Installation

    > sudo apt-get install python-pip
    > sudo pip install --upgrade yujin_tools

### Usage

**cfind**

Code finder. In any directory, simply type `cfind <keyword>` and it will recursively grep to find
any file containing those keywords (also prints line numbers). e.g.

    > cfind CSLAM_MACRO

**yujin_init_workspace**

This creates a catkin style workspace for native and cross-compilations.

    > mkdir my_workspace
    > cd my_workspace
    > yujin_init_workspace

Use wstool to add source repos to the src directory and you'll find 
makefiles in the native/cross directories for parallel building.


## Developing & Packaging ==

    > git clone https://github.com/yujinrobot/yujin_tools.git
    > cd yujin_tools/pip/yujin_tools

* make some changes
* bump the version in `src/yujin_tools/__init__.py
* add a note to the `Changelog`

Finally, upload

    > make build
    > make upload

See Daniel if you need permissions for uploading.
