# genut: C 语言单元测试生成器

基于 **libclang** 的 Python 工具，用于解析 C 源文件并生成 Google Test（GTest）单元测试骨架。支持函数签名提取、分支路径约束提取、圈复杂度驱动的用例生成，以及可选的 stub 代码生成。

## 主要能力

- 基于 AST 的 C 代码分析（类型信息更准确）
- 从 `if / else / switch` 提取路径约束
- 支持按函数过滤生成（`--funcs`）
- 支持从分支条件构造参数（`--construct`）
- 支持 `compile_commands.json`，兼容真实编译参数
- 支持可配置命名、默认值、版权头、额外 include
- 支持宏式 stub 框架（`--stub-framework macro`）

## 安装

### 依赖

- Python 3.7+
- LLVM/Clang（需可访问 libclang 动态库）
- Python 包：

```bash
pip install libclang fastmcp
```

### 生成编译数据库

```bash
# CMake
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..

# Make（使用 Bear）
bear -- make
```

## 快速开始

```bash
# 基础生成
python gen_ut.py --compdb compile_commands.json --src src/basic_functions.c

# 仅针对指定函数
python gen_ut.py --compdb compile_commands.json --src src/basic_functions.c --funcs "add;sub"

# 从分支条件构造参数
python gen_ut.py --compdb compile_commands.json --src src/control_flow.c --construct

# 启用宏式 stub 生成
python gen_ut.py --compdb compile_commands.json --src src/stub_dependency.c --construct --stub-framework macro
```

## Claude Code 集成

克隆项目后用 Claude Code 打开，MCP 服务和 `/genut` skill 会自动生效，无需额外配置。

### MCP 服务

项目通过 `.mcp.json` 注册 MCP 服务，Claude Code 自动发现并启动。可用工具：

| 工具 | 功能 |
| --- | --- |
| `generate_tests` | 生成指定 C 源文件的 GTest 单元测试 |

输出文件：
- `ut_<module>.h` — extern "C" 声明 + stub 声明
- `ut_<module>.cpp` — GTest 测试用例
- `ut_<module>_stub.cpp` — Stub 实现（启用 stub_framework 时）

### /genut Skill

在 Claude Code 中直接使用 `/genut` 触发测试生成：

```
/genut <source_file> [project_root] [outdir] [functions]
```

| 参数 | 说明 |
| --- | --- |
| `source_file` | C 源文件路径（必需） |
| `project_root` | 项目根目录；不填则询问 |
| `outdir` | 测试文件输出目录；不填则询问 |
| `functions` | 目标函数列表，分号分隔；不填则生成全部 |

也可以直接用自然语言（"帮我给这个文件生成单元测试"），Claude 会自动触发 skill。

## 命令行参数

| 参数 | 说明 |
|---|---|
| `--compdb` | `compile_commands.json` 路径（必需） |
| `--src` | C 源文件路径（必需） |
| `--funcs` | 目标函数列表，分号分隔；空表示全部 |
| `--outdir` | 输出目录；默认源文件所在目录 |
| `--construct` | 从分支条件构造参数 |
| `--project-root` | 显式指定项目根目录（用于内部头文件识别） |
| `--config`, `-c` | JSON 配置文件路径 |
| `--compiler` | 系统 include 路径检测编译器：`auto` / `gcc` / `clang` |
| `--stub-framework` | 打桩框架（当前支持 `macro`） |

## 配置（utgen.json）

支持的核心配置项：

- `naming`：文件前后缀、suite 后缀、测试名模板
- `default_values`：基础类型与自定义类型默认值
- `basic_type_keywords`：基本类型关键字扩展
- `compiler`：编译器检测策略
- `copyright_header`
- `extra_includes`

示例：

```json
{
  "naming": {
    "file_prefix": "ut_",
    "suite_suffix": "Test",
    "test_name_pattern": "{func}_Path{index}"
  },
  "default_values": {
    "int_default": "0",
    "pointer_default": "NULL",
    "custom_type_defaults": {
      "Handle": "INVALID_HANDLE_VALUE"
    }
  },
  "compiler": "auto",
  "extra_includes": [
    "<test_helpers.h>",
    "\"project_test_macros.h\""
  ]
}
```

## Stub 机制（可选）

启用 `--stub-framework macro` 时，会额外分析被测函数中的外部调用，并生成对应 stub 代码。

当前限制：

- 仅支持直接函数调用（不支持函数指针调用）
- 宏展开后的复杂调用识别有限

## 示例项目

仓库内置 `test_c_project/` 用于验证生成器行为。

当前示例源文件：

- `basic_functions.c`
- `control_flow.c`
- `error_handling.c`
- `memory_management.c`
- `nested_struct_test.c`
- `param_combo.c`
- `stub_dependency.c`

构建：

```bash
# Windows PowerShell
cd test_c_project
.\build.ps1

# 或 Unix/Git Bash
./build.sh
```

基于示例生成测试：

```bash
python gen_ut.py --compdb test_c_project/compile_commands.json --src test_c_project/src/control_flow.c --outdir test_c_project/tests
```

## 限制

1. 当前仅支持 C 源文件（不支持 C++ 源）
2. 约束求解以常见比较表达式为主，复杂表达式支持有限
3. 复杂宏可能影响分支识别准确性

## 故障排除

- **`libclang not found`**：设置 `LIBCLANG_PATH`
- **找不到编译参数**：确认 `compile_commands.json` 存在且路径正确
- **头文件解析异常**：尝试补充 `--project-root`

## 许可证

[MIT](LICENSE)
