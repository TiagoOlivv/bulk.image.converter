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
	@echo "  make build-win - Build the application for Windows"
	@echo "  make build-linux - Build the application for Linux"
	@echo "  make build-mac - Build the application for macOS"

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

	.PHONY: build-win build-linux build-mac

build-win:
	pyinstaller --noconfirm --onefile --windowed main.py --name bulk_image_converter

build-linux:
	pyinstaller --noconfirm --onefile --windowed main.py --name bulk-image-converter
	fpm -s dir -t deb -n bulk-image-converter -v 1.0 dist/bulk-image-converter=/usr/local/bin/bulk-image-converter

build-mac:
	python setup.py py2app
	hdiutil create dist/bulk-image-converter.dmg -volname "BulkImageConverter" -srcfolder dist/bulk.image.converter.app