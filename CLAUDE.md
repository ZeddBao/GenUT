# gen_ut.py

Generates GTest unit tests from C source files using libclang. Extracts function signatures, cyclomatic complexity, branch paths, and generates tests with parameter constraints.

## Quick Start

```bash
python gen_ut.py --compdb compile_commands.json --src src/file.c 
    [--construct] [--outdir test/] [--funcs "func1;func2"] [--project-root .]
    [--stub-framework macro] [--config utgen.json]
```

Build test project:

```bash
cd test_c_project
./build.sh          # Unix
.\build.ps1         # Windows
```

## Architecture

- `PathConstraint` — Parameter constraints per test path
- `FunctionInfo` — Extracted function metadata
- `CompDbParser` — Parse compile_commands.json
- `CSourceAnalyzer` — libclang integration
- `ConstraintExtractor` — Extract branch conditions
- `GTestBuilder` — Generate .h/.cpp files
- `StubBuilder` — Generate stub implementations
- `GeneratorConfig` — Configuration (naming, defaults, headers)
- `UTGeneratorApp` — CLI entry point

## Output Format

Default: `ut_<module>.h/cpp`, `ut_<module>_stub.cpp`

- `.h`: extern "C" + stub declarations
- `.cpp`: GTest cases with INSTALL_STUB/UNINSTALL_STUB
- `_stub.cpp`: Stub implementations (optional)

## Dependencies

- Python `clang` package
- LLVM/Clang with libclang
- CMake, GCC/Clang compiler
- Google Test framework
