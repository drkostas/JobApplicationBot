# Makefile for the template_python_project

SHELL=/bin/bash
PYTHON_VERSION=3.6
PYTHON_BIN=venv/bin/
TESTS_FOLDER=tests
#--------------------------------------------
ifeq ($(server),prod)
	AN_ENVIRONMENT_SPECIFIC_VARIABLE='production'
	SETUP_FLAG=''
	DEBUG=False
else ifeq ($(server),dev)
	AN_ENVIRONMENT_SPECIFIC_VARIABLE='development'
	SETUP_FLAG=''
	DEBUG=True
else ifeq ($(server),local)
	AN_ENVIRONMENT_SPECIFIC_VARIABLE='local'
	SETUP_FLAG='--local'
	DEBUG=True
else
	AN_ENVIRONMENT_SPECIFIC_VARIABLE='production'
	SETUP_FLAG=
	DEBUG=True
endif
#--------------------------------------------


all:
	$(MAKE) help
help:
	@echo
	@echo "-----------------------------------------------------------------------------------------------------------"
	@echo "                                              DISPLAYING HELP                                              "
	@echo "-----------------------------------------------------------------------------------------------------------"
	@echo "make delete_venv"
	@echo "       Delete the current venv"
	@echo "make create_venv"
	@echo "       Create a new venv for the specified python version"
	@echo "make requirements"
	@echo "       Upgrade pip and install the requirements"
	@echo "make run_tests"
	@echo "       Run all the tests from the specified folder"
	@echo "make setup"
	@echo "       Call setup.py install"
	@echo "make clean_pyc"
	@echo "       Clean all the pyc files"
	@echo "make clean_build"
	@echo "       Clean all the build folders"
	@echo "make clean"
	@echo "       Call delete_venv clean_pyc clean_build"
	@echo "make install"
	@echo "       Call clean create_venv requirements run_tests setup"
	@echo "make help"
	@echo "       Display this message"
	@echo "-----------------------------------------------------------------------------------------------------------"
install:
	$(MAKE) clean
	$(MAKE) create_venv
	$(MAKE) requirements
	$(MAKE) run_tests
	$(MAKE) setup
clean:
	$(MAKE) delete_venv
	$(MAKE) clean_pyc
	$(MAKE) clean_build
delete_venv:
	@echo "Deleting venv.."
	rm -rf venv
create_venv:
	@echo "Creating venv.."
	python$(PYTHON_VERSION) -m venv ./venv
requirements:
	@echo "Upgrading pip.."
	$(PYTHON_BIN)pip install --upgrade pip wheel setuptools
	@echo "Installing requirements.."
	$(PYTHON_BIN)pip install -r requirements.txt
run_tests:
	source $(PYTHON_BIN)activate && \
	export PYTHONPATH=$(PWD) && \
	cd tests && python -m unittest
setup:
	$(PYTHON_BIN)python setup.py install $(SETUP_FLAG)
clean_pyc:
	@echo "Cleaning pyc files.."
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete
clean_build:
	@echo "Cleaning build directories.."
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

.PHONY: delete_venv create_venv requirements run_tests setup clean_pyc clean_build clean help