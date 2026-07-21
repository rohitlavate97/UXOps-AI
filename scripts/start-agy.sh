#!/usr/bin/env bash
# ==============================================================================
# UXOps AI — Antigravity CLI Launcher (POSIX Shell / macOS / Linux)
# ==============================================================================
# This script launches the Antigravity CLI (`agy`) from the root of the UXOps AI
# repository. It resolves the project root directory automatically so it can be
# executed from any working directory.
# ==============================================================================

set -e

# Resolve script directory and locate project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Change working directory to project root
cd "${PROJECT_ROOT}"

echo "======================================================"
echo "🚀 Launching Antigravity CLI for UXOps AI"
echo "📂 Project Root: ${PROJECT_ROOT}"
echo "======================================================"

# Check if 'agy' binary is available in PATH
if ! command -v agy &> /dev/null; then
    echo "❌ Error: 'agy' command (Antigravity CLI) was not found in your PATH."
    echo ""
    echo "To install Antigravity CLI:"
    echo "  Follow instructions at https://antigravity.google/docs/cli"
    echo "  Or ensure the binary is installed and present in your system PATH."
    echo ""
    exit 1
fi

# Pass any extra command-line arguments to agy
echo "Starting Antigravity CLI..."
exec agy "$@"
