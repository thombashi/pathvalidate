BIN_DIR := $(shell pwd)/bin

PYTHON := python3
BIN_CHANGELOG_FROM_RELEASE := $(BIN_DIR)/changelog-from-release

LAST_UPDATE_YEAR := $(shell git log -1 --format=%cd --date=format:%Y)


$(BIN_CHANGELOG_FROM_RELEASE):
	GOBIN=$(BIN_DIR) go install github.com/rhysd/changelog-from-release/v3@latest

.PHONY: build
build: clean
	@$(PYTHON) -m tox -e build
	ls -lh dist/*

.PHONY: changelog
changelog: $(BIN_CHANGELOG_FROM_RELEASE)
	$(BIN_CHANGELOG_FROM_RELEASE) > CHANGELOG.md
	cp -a CHANGELOG.md docs/pages/CHANGELOG.md

.PHONY: check
check:
	$(PYTHON) -m tox -e lint
	-$(PYTHON) -m tox -e lint-examples
	-rm examples/pathvalidate_examples.py

.PHONY: clean
clean:
	rm -rf $(BIN_DIR)
	$(PYTHON) -m tox -e clean

.PHONY: docs
docs:
	@$(PYTHON) -m tox -e docs

.PHONY: idocs
idocs:
	@$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade -e .
	@$(MAKE) docs

.PHONY: fmt
fmt:
	@$(PYTHON) -m tox -e fmt

.PHONY: readme
readme:
	@$(PYTHON) -m tox -e readme

.PHONY: release
release:
	$(PYTHON) -m tox -e release
	$(MAKE) clean

.PHONY: setup-ci
setup-ci:
	$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade pip
	$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade tox

.PHONY: setup-dev
setup-dev: setup-ci
	$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade -e .[test]
	$(PYTHON) -m pip check

.PHONY: test
test:
	$(PYTHON) -m tox -e py

.PHONY: update-copyright
update-copyright:
	sed -i "s/^__copyright__ = .*/__copyright__ = f\"Copyright 2016-$(LAST_UPDATE_YEAR), {__author__}\"/" pathvalidate/__version__.py
	sed -i "s/^Copyright (c) .* Tsuyoshi Hombashi/Copyright (c) 2016-$(LAST_UPDATE_YEAR) Tsuyoshi Hombashi/" LICENSE
