#!/bin/bash
# Start the genut MCP server for use with Claude Code

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON=python3
else
    PYTHON=python
fi

echo "Starting genut MCP server..."
echo "Python: $PYTHON"
echo "Working directory: $SCRIPT_DIR"
echo ""
echo "Available tools:"
echo "  - list_functions: List all functions in a C source file"
echo "  - generate_tests: Generate unit tests for C functions"
echo "  - analyze_function: Analyze a specific function in detail"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the MCP server
$PYTHON mcp_server.py
