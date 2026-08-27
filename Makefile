# DescriptorPin developer tasks. Standard library only, no install needed.
# PYTHONPATH=src lets every target run against the source tree in place.

PYTHON ?= python
export PYTHONPATH := src

.DEFAULT_GOAL := help

.PHONY: help test verify run clean

help: ## Show this help
	@echo "DescriptorPin make targets:"
	@echo "  make test    run the unittest suite"
	@echo "  make verify  run the quality gate (scripts/verify.py)"
	@echo "  make run     scan the mutated sample against the sample pin"
	@echo "  make clean   remove caches and build artefacts"

test: ## Run the test suite
	$(PYTHON) -m unittest discover -s tests -v

verify: ## Run the mechanical quality gate
	$(PYTHON) scripts/verify.py

run: ## Demonstrate a scan against the bundled samples
	$(PYTHON) -m DescriptorPin scan samples/inventory_mutated.json -p samples/pin.json

clean: ## Remove caches and build artefacts
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]"
	$(PYTHON) -c "import shutil; shutil.rmtree('build', ignore_errors=True); shutil.rmtree('dist', ignore_errors=True)"
