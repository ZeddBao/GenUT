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

# Use stub framework with macro-based stubbing
python gen_ut.py --compdb compile_commands.json --src src/file.c --construct --stub-framework macro

# Use custom configuration file
python gen_ut.py --config utgen.json --compdb compile_commands.json --src src/file.c
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
| `PathConstraint` | Stores parameter constraints for a test path, including stub constraints |
| `FunctionInfo` | Holds extracted function metadata (name, return type, params, complexity, paths) |
| `CompDbParser` | Parses `compile_commands.json` to extract compiler arguments |
| `CSourceAnalyzer` | Uses libclang to parse C source and extract function info |
| `ConstraintExtractor` | Extracts if/switch branch conditions and function call constraints |
| `GTestBuilder` | Generates GTest-compatible `.cpp` and `.h` files with configurable naming and defaults |
| `StubFrameworkBase` | Abstract base class for stub frameworks (macro-based implementation included) |
| `StubBuilder` | Generates stub function declarations and implementations |
| `GeneratorConfig` | Configuration class for naming, default values, copyright headers, extra includes |
| `UTGeneratorApp` | Main entry point with CLI argument handling |

### Output Files

Generated test files follow this naming convention (configurable via `naming` config):

- `<prefix><module><suffix>.h` - Header with `extern "C"` function declarations and stub declarations
- `<prefix><module><suffix>.cpp` - GTest test cases (with `INSTALL_STUB`/`UNINSTALL_STUB` when using stub framework)
- `<prefix><module><suffix>_stub.cpp` - Stub function implementations (when using `--stub-framework`)

Default naming: `ut_<module>.h`, `ut_<module>.cpp`, `ut_<module>_stub.cpp`

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
