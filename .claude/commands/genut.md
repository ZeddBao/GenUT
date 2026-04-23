---
name: genut
description: Generate GTest unit tests for a C source file. Use when the user says "generate tests", "生成ut", "生成单元测试", or provides a .c file path and asks for tests.
arguments: [source_file, project_root, outdir, functions]
allowed-tools: Glob, Read, Edit, mcp__genut__generate_tests
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
6. Ask the user: "是否需要对生成的测试文件进行 LLM 审查和修复？(y/n)"
   - If the answer is no, skip to step 7.
   - If the answer is yes, read the generated `.h` and `.cpp` files, as well as the original `$source_file`, then review and fix the following issues using Edit:

   **参数构造**
   - 参数类型与实际函数签名不匹配（如指针未取地址、数组未初始化）
   - 结构体/联合体字段赋值不完整，缺少必填字段
   - 枚举值使用了字面量整数而非枚举常量

   **Stub**
   - stub 函数签名与被桩函数的实际签名不一致
   - stub 返回值类型或默认返回值不正确
   - 应当被桩的外部函数调用未被覆盖

   **校验点**
   - 返回值断言缺失或使用了错误的 GTest 宏（如对指针用 `EXPECT_EQ` 而非 `EXPECT_NE(nullptr, ...)`）
   - 副作用（输出参数、全局变量修改）未被断言
   - 死代码路径（永远无法触达的条件分支）的测试用例

   修复时只改有问题的地方，不重写整个文件。

7. Report the output files, the number of functions/test paths generated, and a summary of fixes made.
