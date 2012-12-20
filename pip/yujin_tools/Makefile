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
	@echo "  deb_distro: build the distribution tarball."
	@echo "  ppa       : upload to the launchpad ppa."
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

distro:
	python setup.py sdist

deb_distro:
	python setup.py --command-packages=stdeb.command sdist_dsc bdist_deb

register:
	python setup.py register

pypi: 
	python setup.py sdist upload

ppa:
	dput -u ppa:yujinrobot/ppa deb_dist/yujin-tools_${VERSION}-1_amd64.changes	

clean:  clean_dist
	echo "clean"

