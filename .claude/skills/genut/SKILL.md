---
name: genut
description: Generate GTest unit tests for a C source file. Use when the user says "generate tests", "生成ut", "生成单元测试", or provides a .c file path and asks for tests.
arguments: [source_file, project_root, outdir, functions]
allowed-tools: Glob, mcp__genut__generate_tests
---

Generate GTest unit tests for `$source_file`.

Steps:
1. Resolve the absolute path of `$source_file`.
2. Determine `project_root`:
   - If `$project_root` is provided, use it (resolve to absolute path).
   - Otherwise, ask the user: "请指定项目根目录（含 `compile_commands.json` 或 `CMakeLists.txt` 的目录）："，wait for the reply, then use that path.
3. Find `compile_commands.json` inside `$project_root` or its common build subdirectories (`build/`, `cmake-build-debug/`, `cmake-build-release/`).
4. Determine `outdir`:
   - If `$outdir` is provided, use it (resolve to absolute path).
   - Otherwise, ask the user: "请指定测试文件输出目录（例如 `tests/`）："，wait for the reply, then use that path.
5. Call `mcp__genut__generate_tests` with:
   - `source_file`: absolute path from step 1
   - `compdb`: absolute path from step 3
   - `project_root`: from step 2
   - `outdir`: from step 4
   - `construct`: true
   - `stub_framework`: `"macro"`
   - If `$functions` is provided, pass it as `functions` (semicolon-separated list of function names).
6. Report the output files and the number of functions/test paths generated.
