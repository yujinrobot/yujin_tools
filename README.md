Yujin Tools
=========



Utilies for yujin development. These are system tools (i.e. not deployed within a 
ros environment).

Template style wizard shortcuts for creating ros packages, stacks.

## Tools

* cfind 
* yujin_init_workspace
* yujin_init_build
* yujin_make, yujin_make_isolated

## Usage

### Installation

    > sudo apt-get install python-pip
    > sudo pip install --upgrade yujin_tools

### Usage

**cfind**

Code finder. In any directory, simply type `cfind <keyword>` and it will recursively grep to find
any file containing those keywords (also prints line numbers). e.g.

    > cfind CSLAM_MACRO

**yujin_init_workspace**, **yujin_init_buld**, **yujin_make**, **yujin_make_isolated**

* [Yujin Init Tools](https://github.com/yujinrobot/yujin_tools/wiki/yujin-init)

## Developing & Packaging

    > git clone https://github.com/yujinrobot/yujin_tools.git
    > cd yujin_tools

* make some changes
* bump the version in `src/yujin_tools/__init__.py
* add a note to the `Changelog`

Finally, upload

    > make build
    > make upload

See Daniel if you need permissions for uploading.
