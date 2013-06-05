# DescriptorPin developer tasks. Standard library only, no install needed.
# PYTHONPATH=src lets every target run against the source tree in place.

PYTHON ?= python
export PYTHONPATH := src

.DEFAULT_GOAL := help

.PHONY: help test verify run clean

help: ## Show this help
	@echo "DescriptorPin make targets:"
	@echo "  make test    run the unittest suite"
