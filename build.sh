#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright
pip install playwright

# Install Playwright browsers and dependencies
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright playwright install chromium
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright playwright install-deps chromium

# Make the browser directory accessible
chmod -R 777 /opt/render/.cache/ms-playwright
