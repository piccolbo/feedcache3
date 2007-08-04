#
# $Id$
#

SVNHOME=$(shell svn info | grep "^URL" | cut -f2- -d: | sed 's/^ //')
PROJECT=FeedCache
VERSION=$(shell basename $(SVNHOME))
RELEASE=$(PROJECT)-$(VERSION)

help:
	@echo "package - build source distro"
	@echo "register - update pypi index"

package: setup.py
	python setup.py sdist --force-manifest
	mv dist/*tar.gz ~/Desktop/

register: setup.py
	python setup.py register

%: %.in
	cat $< | sed 's/VERSION/$(VERSION)/g' > $@

tags:
	find . -name '*.py' | etags -l auto --regex='/[ \t]*\def[ \t]+\([^ :(\t]+\)/\1/' -
