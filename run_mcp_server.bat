@echo off
REM Start the genut MCP server for use with Claude Code

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo Starting genut MCP server...
echo Python: python
echo Working directory: %SCRIPT_DIR%
echo.
echo Available tools:
echo   - list_functions: List all functions in a C source file
echo   - generate_tests: Generate unit tests for C functions
echo   - analyze_function: Analyze a specific function in detail
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the MCP server
python mcp_server.py

endlocal
