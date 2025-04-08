VENV_PATH := venv
PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip

.PHONY: help setup run clean build

help:
	@echo "Makefile commands:"
	@echo "  make setup   - Create virtual environment and install dependencies"
	@echo "  make run     - Run the application"
	@echo "  make clean   - Remove virtual environment and build artifacts"
	@echo "  make freeze  - Freeze dependencies to requirements.txt"
	@echo "  make build-linux - Build the application for Linux"

setup:
	python3 -m venv $(VENV_PATH)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	source venv/bin/activate

run:
	$(PYTHON) main.py

clean:
	rm -rf $(VENV_PATH) dist build __pycache__ *.spec

freeze:
	$(PIP) freeze > requirements.txt

build-linux:
	venv/bin/pyinstaller --noconfirm --onefile --windowed main.py --name bulk-image-converter
