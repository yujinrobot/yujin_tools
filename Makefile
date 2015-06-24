VERSION=`./setup.py --version`
FILE_EXISTS:=$(wildcard install.record)
ifeq ($(strip $(FILE_EXISTS)),)
    UNINSTALL_FILES:=
else
    UNINSTALL_FILES:=$(shell cat install.record)
endif
 

help:
	@echo "Local Build"
	@echo "  build     : build the python package."
	@echo "  install   : install the python package into /usr/local."
	@echo "  uninstall : uninstall the python package from /usr/local."
	@echo "Pypi package"
	@echo "  register  : register the package with PyPI."
	@echo "  distro    : build the distribution tarball."
	@echo "  pypi      : upload the package to PyPI."
	@echo "Deb package"
	@echo "  deb_deps  : install the package builder dependencies (fpm)."
	@echo "  deb       : build the deb."
	@echo "  upload_deb: upload to yujin's repository."
	@echo "  release   : make pypi package and deb release together."
	@echo "Other"
	@echo "  clean     : clean build/dist directories."

build:
	python setup.py build

# Another install method that might be better:
#       sudo checkinstall python setup.py install
install: distro
	sudo python setup.py install --record install.record

uninstall:
	sudo rm -f ${UNINSTALL_FILES}

setup:
	echo "building version ${VERSION}"

clean_dist:
	-rm -f MANIFEST
	-rm -rf build dist
	-rm -rf deb_dist
	-rm -rf debian
	-rm -rf ../*.build
	-rm -rf ../*.gz

distro:
	python setup.py sdist

# the following needs stddeb installed
source_deb:
	python setup.py --command-packages=stdeb.command sdist_dsc

deb_distro:
	python setup.py --command-packages=stdeb.command sdist_dsc bdist_deb

register:
	python setup.py register

pypi: 
	python setup.py sdist upload

deb_deps:
	sudo apt-get install ruby-dev build-essential
	sudo gem install fpm

deb:
	rm *.deb
	fpm -f -s python -t deb yujin_tools

upload_deb:
	./scripts/upload_deb

clean_deb:
	rm *.deb

release: pypi deb upload_deb

clean:  clean_dist clean_deb
	-sudo rm -f install.record
	-sudo rm -rf build
	-sudo rm -rf yujin_tools.egg-info

