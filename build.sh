#!/bin/bash
# HIPAA-Lockdown-CLI: Build Script
# Compiles the Python application into a standalone USB-runnable Linux executable.

set -e

echo "=========================================="
echo " HIPAA-Lockdown Standalone Compilation    "
echo " (System-Site-Packages Architecture)      "
echo "=========================================="

echo "1. Preparing Virtual Environment..."
cd "$(dirname "$0")"

# Remove old venv and dist
rm -rf venv dist build *.spec

# Use system site packages so we inherit 'gi' from the host 'python3-gi'
# This entirely prevents needing 'gcc' to compile PyGObject/cairo from source!
python3 -m venv --system-site-packages venv
source venv/bin/activate

echo "2. Installing PyInstaller..."
pip install --upgrade pip
pip install pyinstaller

echo "3. Freezing CLI Application..."
# Create the CLI executable (headless)
pyinstaller --onefile \
    --name hipaa-lockdown-cli \
    --workpath build/cli \
    --specpath build/cli \
    --clean \
    --hidden-import "hipaa_lockdown.modules.auth" \
    --hidden-import "hipaa_lockdown.modules.filesystem" \
    --hidden-import "hipaa_lockdown.modules.audit" \
    --hidden-import "hipaa_lockdown.modules.network" \
    --hidden-import "hipaa_lockdown.modules.scanner" \
    --hidden-import "hipaa_lockdown.core.safety" \
    --hidden-import "hipaa_lockdown.core.system" \
    --hidden-import "hipaa_lockdown.core.legal" \
    hipaa_lockdown/main.py

echo "4. Freezing GTK4 GUI Application..."
# Create the GUI executable (windowed, including GTK dependencies)
pyinstaller --onefile --windowed \
    --name hipaa-lockdown-gui \
    --workpath build/gui \
    --specpath build/gui \
    --clean \
    --hidden-import "gi" \
    --hidden-import "gi.repository.Gtk" \
    --hidden-import "gi.repository.Adw" \
    --hidden-import "gi.repository.Pango" \
    --hidden-import "gi.repository.GObject" \
    --hidden-import "gi.repository.Gio" \
    --hidden-import "gi.repository.GLib" \
    --hidden-import "hipaa_lockdown.modules.auth" \
    --hidden-import "hipaa_lockdown.modules.filesystem" \
    --hidden-import "hipaa_lockdown.modules.audit" \
    --hidden-import "hipaa_lockdown.modules.network" \
    --hidden-import "hipaa_lockdown.modules.scanner" \
    --hidden-import "hipaa_lockdown.core.safety" \
    --hidden-import "hipaa_lockdown.core.system" \
    --hidden-import "hipaa_lockdown.core.legal" \
    --collect-data "gi" \
    --collect-submodules "gi" \
    --collect-all "gi" \
    hipaa_lockdown/gui.py

echo "=========================================="
echo " Compilation Complete!"
echo " The standalone executables have been built in the ./dist directory."
echo " You can now transfer the ./dist folder to your USB drive."
echo "=========================================="
