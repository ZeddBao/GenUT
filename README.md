# genut: C Unit Test Generator

A Python tool that uses libclang to parse C source files and generate Google Test (GTest) unit test skeletons. It extracts function signatures, calculates cyclomatic complexity, identifies branch paths (if/else, switch/case), and generates test cases with parameter constraints.

## Features

- **AST-based analysis**: Uses libclang to parse C source code with full type information
- **Path constraint extraction**: Automatically extracts parameter constraints from if/switch branch conditions
- **Configurable architecture**: Project-specific customizations (naming, defaults, compiler) decoupled from core logic
- **Compilation database support**: Uses `compile_commands.json` for accurate compilation arguments
- **Cyclomatic complexity calculation**: Generates appropriate number of test cases based on function complexity
- **Modular design**: Clean separation of concerns with configuration injection

## Quick Start

### 1. Install Dependencies

```bash
pip install libclang
```

### 2. Prepare Compilation Database

Ensure your C project has a `compile_commands.json` file:

```bash
# For CMake projects
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..

# For Make projects (using Bear)
bear -- make
```

### 3. Generate Unit Tests

```bash
# Generate tests for a source file
python gen_ut.py --compdb compile_commands.json --src src/math_utils.c

# With custom configuration
python gen_ut.py --config utgen.json --compdb compile_commands.json --src src/math_utils.c
```

### 4. Build and Run Tests

```bash
# Compile with GTest
g++ -std=c++11 -I. -I/path/to/gtest/include ut_math_utils.cpp \
    -L/path/to/gtest/lib -lgtest -lgtest_main -o math_utils_test

# Run tests
./math_utils_test
```

## Architecture

The tool has been refactored into a modular architecture with clear separation between generic UT generation functionality and project-specific customizations:

```plain
genut/
├── gen_ut.py           # Main entry script
├── config.py           # Configuration classes (GeneratorConfig, NamingConfig, DefaultValueConfig)
├── models.py           # Data models (PathConstraint, FunctionInfo)
├── compdb.py           # Compilation database parser with compiler auto-detection
├── analyzer.py         # C source analyzer using libclang
├── extractor.py        # Constraint extraction from function AST
├── builder.py          # GTest builder with configurable naming and defaults
├── CLAUDE.md           # Project instructions for Claude Code
└── test_c_project/     # Sample C project for testing
```

### Core Components

| Component | Responsibility |
| ----------- | --------------- |
| **CompDbParser** | Parses `compile_commands.json` to extract compiler arguments with compiler auto-detection |
| **CSourceAnalyzer** | Uses libclang to parse C source and extract function information |
| **ConstraintExtractor** | Extracts if/switch branch conditions, generates path constraints |
| **GTestBuilder** | Generates GTest-compatible `.cpp` and `.h` files with configurable naming and defaults |
| **UTGeneratorApp** | Main entry point with CLI argument handling |

## Installation

### Prerequisites

- Python 3.7+
- LLVM/Clang installation with libclang DLL/library available
- Python package: `clang` (libclang Python bindings)

```bash
pip install clang
```

### System Requirements

- **Windows**: Install LLVM from [llvm.org](https://llvm.org/) or via Chocolatey: `choco install llvm`
- **Linux**: Install via package manager: `sudo apt-get install clang libclang-dev`
- **macOS**: Install via Homebrew: `brew install llvm`

Ensure the libclang library path is in your system PATH or set `LIBCLANG_PATH` environment variable.

## Usage

### Basic Usage

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

### Command Line Options

| Option | Description |
| -------- | ------------- |
| `--compdb` | Path to `compile_commands.json` (required) |
| `--src` | Path to the C source file (required) |
| `--funcs` | Semicolon-separated list of target functions. Leave empty for all. |
| `--outdir` | Output directory for generated files. Defaults to the source file's directory. |
| `--construct` | Construct test parameters from branch conditions. |
| `--project-root` | Explicitly specify the project root directory to correctly identify internal headers. |
| `--config, -c` | Path to JSON configuration file for customizing naming, defaults, etc. |
| `--compiler` | Compiler to use for system include detection (auto, gcc, or clang). |

## Configuration

The tool supports JSON configuration files to customize behavior for different projects. Customizations include:

- **Naming conventions**: File prefixes/suffixes, test suite suffixes, test name patterns
- **Default values**: Type-specific default values (int, float, pointers, structs, custom types)
- **Compiler selection**: Automatic or explicit compiler detection for system includes
- **Type recognition**: Extensible list of basic type keywords

### Configuration File Example

Create `utgen.json`:

```json
{
    "naming": {
        "file_prefix": "test_",
        "file_suffix": "",
        "suite_suffix": "UT",
        "test_name_pattern": "{func}_Path{index}"
    },
    "default_values": {
        "int_default": "0",
        "float_default": "0.0",
        "pointer_default": "nullptr",
        "struct_default": "{}",
        "bool_default": "false",
        "custom_type_defaults": {
            "MyString": "\"\"",
            "Handle": "INVALID_HANDLE_VALUE"
        }
    },
    "basic_type_keywords": [
        "int", "char", "float", "double", "long", "short",
        "bool", "size_t", "unsigned", "signed", "uint8_t", "uint16_t",
        "uint32_t", "uint64_t", "int8_t", "int16_t", "int32_t", "int64_t"
    ],
    "compiler": "auto"
}
```

### Using Configuration

```bash
python gen_ut.py --config utgen.json --compdb compile_commands.json --src src/file.c
```

## How It Works

### 1. Compilation Database Parsing

- Reads `compile_commands.json` to extract compiler arguments
- Auto-detects compiler (gcc/clang) or uses explicit configuration
- Adds system include paths from the detected compiler

### 2. Source Code Analysis

- Uses libclang to parse the C source file into an AST
- Extracts function declarations with parameter types
- Calculates cyclomatic complexity for each function
- Identifies global variable dependencies

### 3. Constraint Extraction

- Traverses function AST to find if/switch statements
- Extracts branch conditions and parameter constraints
- Generates path constraints for each possible execution path
- Handles nested conditions and logical operators

### 4. Test Generation

- Creates a header file with `extern "C"` function declarations
- Generates GTest test cases for each path constraint
- Uses configuration for naming conventions and default values
- Optionally constructs test parameters from branch conditions

### Output Files

With default configuration:

- `ut_<module>.h` - Header with `extern "C"` function declarations
- `ut_<module>.cpp` - GTest test cases

With custom configuration (`file_prefix: "test_"`, `suite_suffix: "UT"`):

- `test_<module>.h` - Header with `extern "C"` function declarations
- `test_<module>.cpp` - GTest test cases with `MathUtilsUT` test suite class

## Test Project

The `test_c_project/` directory contains a sample C project for testing the generator.

### Build Test Project

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

### Generate Tests for Test Project

```bash
# Default configuration
python gen_ut.py --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c --outdir test_c_project/test

# With custom configuration
python gen_ut.py --config utgen.json --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c  --outdir test_c_project/test

# With parameter construction
python gen_ut.py --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c  --outdir test_c_project/test --constructpython gen_ut.py --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c --outdir test_c_project/test

# 自定义配置
python gen_ut.py --config utgen.json --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c  --outdir test_c_project/test

# 使用参数构造
python gen_ut.py --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c  --outdir test_c_project/test --construct
```

## Extending and Customizing

### Adding Custom Type Defaults

Add project-specific types to the configuration:

```json
{
    "default_values": {
        "custom_type_defaults": {
            "MyString": "\"\"",
            "Handle": "NULL",
            "Status": "STATUS_OK",
            "Buffer": "{0}",
            "Config": "DEFAULT_CONFIG"
        }
    }
}
```

### Custom Naming Patterns

Adjust naming patterns to match project conventions:

```json
{
    "naming": {
        "file_prefix": "test_",
        "file_suffix": "_gtest",
        "suite_suffix": "Fixture",
        "test_name_pattern": "Test_{func}_Scenario{index}"
    }
}
```

### Extending Basic Type Recognition

Add project-specific type keywords:

```json
{
    "basic_type_keywords": [
        "int", "char", "float", "double", "long", "short",
        "bool", "size_t", "unsigned", "signed",
        "uint8_t", "uint16_t", "uint32_t", "uint64_t",
        "int8_t", "int16_t", "int32_t", "int64_t",
        "time_t", "ssize_t", "pid_t", "mode_t"
    ]
}
```

## Limitations

1. **C Language Only**: Currently supports C source files only (not C++)
2. **Simple Constraint Solving**: Constraint extraction handles basic comparisons but not complex expressions
3. **Local Variable References**: Cannot automatically resolve local variable references in return expressions
4. **Function Pointers**: Limited support for function pointer types
5. **Complex Macros**: Preprocessor macros are expanded during parsing, may affect branch detection

## Troubleshooting

### Common Issues

**"libclang not found" error:**

```bash
# Set libclang library path
export LIBCLANG_PATH="/path/to/libclang.so"
# Or on Windows
set LIBCLANG_PATH=C:\path\to\libclang.dll
```

**Missing compilation database:**

- Ensure your build system generates `compile_commands.json`
- For CMake: `cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..`
- For Make projects: Use Bear (`bear -- make`)

**Incorrect include paths:**

- Use `--project-root` to specify project root directory
- Check that `compile_commands.json` contains correct paths

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Submit a pull request

### Development Setup

```bash
git clone <repository-url>
cd genut
pip install -r requirements.txt  # If requirements file exists
```

### Running Tests

```bash
# Run integration tests
python -m pytest test/  # If test directory exists

# Test with sample project
cd test_c_project
./build.sh
cd ..
python gen_ut.py --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c
```

## License

[MIT License](LICENSE)

## Acknowledgments

- Built on [libclang](https://clang.llvm.org/docs/Tooling.html) for C/C++ parsing
- Generates tests for [Google Test](https://github.com/google/googletest) framework
- Inspired by various unit test generation tools and research
