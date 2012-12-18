Yujin Tools
=========

Utilies for yujin development. These are system tools (i.e. not deployed within a 
ros environment).

Template style wizard shortcuts for creating ros packages, stacks.

## Tools

* cfind 
* yujin_init_workspace

## Usage

### Installation

    > sudo apt-get install python-pip
    > sudo pip install --upgrade yujin_tools

## Development

    > git clone https://github.com/yujinrobot/yujin_tools.git
    > cd yujin_tools/pip/yujin_tools

* make some changes
* bump the version in `src/yujin_tools/__init__.py
* add a note to the `Changelog`
* upload

    > make build
    > make upload

See Daniel if you need permissions for uploading.
