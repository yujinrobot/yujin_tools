
FILE_EXISTS:=$(wildcard install.record)
ifeq ($(strip $(FILE_EXISTS)),)
    UNINSTALL_FILES:=
else
    UNINSTALL_FILES:=$(shell cat install.record)
endif
 

help:
	@echo "  build    : build the python package."
	@echo "  install  : install the python package into /usr/local."
	@echo "  uninstall: uninstall the python package from /usr/local."
	@echo "  distro   : build the distribution tarball."
	@echo "  register : register the package with PyPI."
	@echo "  upload   : upload the package to PyPI."
	@echo "  clean    : clean build/dist directories."

build:
	python setup.py build

install:
	sudo python setup.py install --record install.record

# Use -f to ignore any warnings about it being an empty argument
uninstall:
	sudo rm -f ${UNINSTALL_FILES}

distro:
	python setup.py sdist

register:
	python setup.py register

upload:
	python setup.py sdist upload

clean:
	rm -rf build dist MANIFEST

