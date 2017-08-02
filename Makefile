#!/usr/bin/make
# WARN: gmake syntax
########################################################
#
# useful targets:
#   make test   - run the unit tests
#   make flake8 - linting and pep8
#   make docs 	- create manpages and html documentation
#   make loc 	- stats about loc

########################################################
# variable section

NAME = vulnserver
OS = $(shell uname -s)
PYTHON = $(shell which python3)
VIRTUALENV_PATH = $(shell echo $$HOME/.virtualenvs)
INSTALL_PATH = /usr/local/lib
EXEC_PATH = /usr/local/bin

MANPAGES=$(wildcard docs/man/**/*.*.ronn)
MANPAGES_GEN=$(patsubst %.ronn,%,$(MANPAGES))
MANPAGES_HTML=$(patsubst %.ronn,%.html,$(MANPAGES))
ifneq ($(shell which ronn 2>/dev/null),)
RONN2MAN = ronn
else
RONN2MAN = @echo "ERROR: 'ronn' command is not installed but is required to build $(MANPAGES)" && exit 1
endif

UNITTESTS=unittest
COVERAGE=coverage

########################################################


docs: $(MANPAGES)
	$(RONN2MAN) $^

.PHONY: clean
clean:
	rm -f $(MANPAGES_GEN) $(MANPAGES_HTML)
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./*.egg-info
	rm -rf ./*.deb
	rm -rf .tox
	rm -rf .coverage
	rm -rf .sloccount
	rm -rf .cache
	find . -name '*.pyc.*' -delete
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

loc:
	mkdir -p .sloccount
	sloccount --datadir .sloccount $(NAME)/lib $(NAME)/cli | grep -v SLOCCount | grep -v license | grep -v "see the documentation"

flake8:
	@echo "#############################################"
	@echo "# Running flake8 Compliance Tests"
	@echo "#############################################"
	-flake8 --ignore=E501,E221,W291,W391,E302,E251,E203,W293,E231,E303,E201,E225,E261,E241 $(NAME)/lib $(NAME)/cli

test:
	py.test --cov-report term --cov=$(NAME) ./tests/*

virtualenv:
	mkdir -p $(VIRTUALENV_PATH)
	rm -rf $(VIRTUALENV_PATH)/$(NAME)
	virtualenv -p $(PYTHON) $(VIRTUALENV_PATH)/$(NAME)

virtualenv-install: virtualenv
	$(VIRTUALENV_PATH)/$(NAME)/bin/python setup.py install

virtualenv-develop: virtualenv
	# hack no idea why this isn't working
	$(VIRTUALENV_PATH)/$(NAME)/bin/pip install numpy scipy
	$(VIRTUALENV_PATH)/$(NAME)/bin/python3 setup.py develop

virtualenv-sdist: virtualenv
	$(VIRTUALENV_PATH)/$(NAME)/bin/python setup.py sdist

install:
	cp -r $(VIRTUALENV_PATH)/$(NAME) $(INSTALL_PATH)/$(NAME)
	ln -f -s $(INSTALL_PATH)/$(NAME)/bin/$(NAME) $(EXEC_PATH)/$(NAME)

container:
	bash ./scripts/build.sh -d
	bash ./scripts/build.sh -b

all: docs flake8 test loc
