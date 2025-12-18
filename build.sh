#!/bin/bash
# Build script for creating platform-specific binaries

set -e

echo "Building ACP-Letta Bridge binaries..."

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build for current platform
pyinstaller --onefile \
    --name acp-letta-bridge \
    --add-data "config.py:." \
    acp_letta_bridge.py

echo "Build complete! Binary: dist/acp-letta-bridge"
echo ""
echo "To build for other platforms, use:"
echo "  - Docker with cross-compilation"
echo "  - GitHub Actions with matrix builds"
echo "  - Platform-specific build machines"