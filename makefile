#!make

SHELL = /bin/sh

# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

# OS and CPU
OS := $(shell uname -s)
CPU := $(shell uname -m)
ifeq ($(OS), Darwin)
	ifeq ($(CPU), arm64)
		PLATFORM := MacM1
	else
		PLATFORM := MacIntel
	endif
else
	PLATFORM := Linux
endif

# -- Setup Commands --------------- --- --  -

install: install-x86 install-pre-commit

install-x86:
	@python3.9 -m pip install -U tox pre-commit
	@python3.9 -m venv venv
	@venv/bin/pip install -U pip setuptools wheel
	@venv/bin/pip install -r requirements.txt -e .

## Install git hooks that run Flake8 before accepting commits.
install-pre-commit:
# 	@git lfs install
	@pre-commit install -f --install-hook && \
	git config --bool flake8.strict true && \
	git config --bool flake8.lazy true

ci-venv:
	@pre-commit run --from-ref origin/master --to-ref HEAD
	@git diff --name-only origin/master HEAD | grep CHANGELOG.rst || (echo missing CHANGELOG && exit 1)
	@echo mypy && venv/bin/mypy src/ocore tests
	@echo pytest && venv/bin/pytest

# -- Wrapup --------------- --- --  -
