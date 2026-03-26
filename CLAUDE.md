# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**gen_ut.py** is a Python tool that uses libclang to parse C source files and generate Google Test (GTest) unit test skeletons. It extracts function signatures, calculates cyclomatic complexity, identifies branch paths (if/else, switch/case), and generates test cases with parameter constraints.

## Commands

### Generate Unit Tests

```bash
# Generate tests for a C source file
python gen_ut.py --compdb <compile_commands.json> --src <source_file.c>

# With parameter construction from branch conditions
python gen_ut.py --compdb compile_commands.json --src src/file.c --construct

# Output to specific directory
python gen_ut.py --compdb compile_commands.json --src src/file.c --outdir test/

# Target specific functions only
python gen_ut.py --compdb compile_commands.json --src src/file.c --funcs "func1;func2"

# Specify project root for internal header detection
python gen_ut.py --compdb compile_commands.json --src src/file.c --project-root /path/to/project
```

### Build Test C Project

The `test_c_project/` directory contains a sample C project for testing the generator.

**Windows (PowerShell):**

```bash
cd test_c_project
.\build.ps1          # Build
.\build.ps1 clean   # Clean
```

**Unix/Git Bash:**

```bash
cd test_c_project
./build.sh          # Build
./build.sh clean    # Clean
```

Build outputs:

- Binary: `build/test_c_project.exe`
- Compilation database: `compile_commands.json` (used by libclang)

## Architecture

### Main Tool: gen_ut.py

Single-file Python application with these key classes:

| Class | Responsibility |
|-------|---------------|
| `PathConstraint` | Stores parameter constraints for a test path |
| `FunctionInfo` | Holds extracted function metadata (name, return type, params, complexity, paths) |
| `CompDbParser` | Parses `compile_commands.json` to extract compiler arguments |
| `CSourceAnalyzer` | Uses libclang to parse C source and extract function info |
| `ConstraintExtractor` | Extracts if/switch branch conditions, generates path constraints |
| `GTestBuilder` | Generates GTest-compatible `.cpp` and `.h` files |
| `UTGeneratorApp` | Main entry point with CLI argument handling |

### Output Files

Generated test files follow this naming convention:

- `ut_<module>.h` - Header with `extern "C"` function declarations
- `ut_<module>.cpp` - GTest test cases

### Test Project Structure

```
test_c_project/
├── include/           # C headers
├── src/               # C source files (input for generator)
├── test/              # Generated test output
├── build/             # Build artifacts
└── compile_commands.json  # Required for libclang parsing
```

## Dependencies

- **Python**: `clang` package (libclang Python bindings)
- **External**: LLVM/Clang installation with libclang DLL/library available
- **Build tools**: CMake, GCC or Clang compiler
- **Test framework**: Google Test (for running generated tests)
