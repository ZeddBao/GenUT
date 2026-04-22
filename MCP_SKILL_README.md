# Genut MCP Skill

一个 FastMcp 服务器，提供自动生成 C 代码单元测试的功能。该 skill 可以被 Claude agents 调用。

## 功能

### 1. `list_functions` - 列出源文件中的所有函数

分析 C 源文件并列出所有函数及其元数据。

**参数：**
- `source_file` (必需): C 源文件路径
- `compdb` (可选): 编译数据库文件路径 (compile_commands.json)
- `project_root` (可选): 项目根目录

**返回值：**
```json
{
  "file": "path/to/file.c",
  "functions": [
    {
      "name": "function_name",
      "return_type": "int",
      "parameters": [...],
      "cyclomatic_complexity": 3,
      "global_vars": [...]
    }
  ],
  "count": 5
}
```

### 2. `generate_tests` - 为指定函数生成单元测试

生成 GTest 格式的单元测试代码。

**参数：**
- `source_file` (必需): C 源文件路径
- `compdb` (必需): 编译数据库文件路径
- `functions` (可选): 分号分隔的函数名列表。如果省略，为所有函数生成测试
- `outdir` (可选): 输出目录 (默认: 与源文件相同目录)
- `construct` (可选): 是否生成构造的测试用例 (默认: true)
- `stub_framework` (可选): stub 框架类型 (如 'macro')
- `config_file` (可选): 配置文件路径 (utgen.json)
- `project_root` (可选): 项目根目录

**返回值：**
```json
{
  "success": true,
  "source_file": "path/to/file.c",
  "functions_generated": 3,
  "function_names": ["func1", "func2", "func3"],
  "output_files": {
    "header": "path/to/ut_file.h",
    "implementation": "path/to/ut_file.cpp",
    "stubs": ["path/to/ut_file_stub.cpp"]
  },
  "total_test_paths": 12,
  "test_paths_per_function": {
    "func1": 4,
    "func2": 4,
    "func3": 4
  }
}
```

### 3. `analyze_function` - 分析特定函数的结构和约束

显示函数的详细分析，包括参数、测试路径和约束。

**参数：**
- `source_file` (必需): C 源文件路径
- `compdb` (必需): 编译数据库文件路径
- `function_name` (必需): 要分析的函数名
- `project_root` (可选): 项目根目录

**返回值：**
```json
{
  "name": "function_name",
  "return_type": "int",
  "cyclomatic_complexity": 3,
  "parameters": [...],
  "global_variables": {...},
  "test_paths": 4,
  "paths": [
    {
      "index": 1,
      "description": "path condition",
      "expected_return": "value",
      "parameter_values": {...}
    }
  ]
}
```

## 安装

### 先决条件

```bash
# 安装依赖
pip install -r requirements.txt
```

### 配置

MCP 服务器已通过 `.mcp.json` 配置在项目中。Claude Code 会自动发现并加载它。

## 使用示例

### 列出所有函数

```
Agent: 
请列出 test_c_project/src/control_flow.c 中的所有函数

Claude:
使用 list_functions 工具列出源文件中的所有函数。
```

### 生成测试

```
Agent:
为 test_c_project/src/control_flow.c 中的 macro_defined_condition_test 和 
multiple_macro_conditions 函数生成单元测试
```

### 分析特定函数

```
Agent:
分析 test_c_project/src/control_flow.c 中的 macro_defined_condition_test 函数的结构
```

## 工作流程

### 典型的 Agent 工作流程

1. **列出函数** - Agent 首先使用 `list_functions` 探索可用的函数
2. **选择函数** - Agent 根据复杂度或其他标准选择要测试的函数
3. **分析函数** - 使用 `analyze_function` 了解约束和测试路径
4. **生成测试** - 使用 `generate_tests` 生成测试代码
5. **验证结果** - Agent 检查生成的测试文件

## 输出文件

生成的测试文件会保存到指定的输出目录：

- `ut_<module>.h` - 头文件，包含 extern "C" 声明和 stub 函数声明
- `ut_<module>.cpp` - C++ 实现文件，包含 GTest 测试用例
- `ut_<module>_stub.cpp` (可选) - stub 函数实现

## 配置文件 (utgen.json)

可以使用配置文件自定义代码生成行为：

```json
{
  "naming": {
    "file_prefix": "ut_",
    "file_suffix": "",
    "suite_suffix": "Suite",
    "test_name_pattern": "{func}_Path{index}"
  },
  "default_values": {
    "int_default": "0",
    "float_default": "0.0f",
    "pointer_default": "nullptr"
  },
  "extra_includes": [
    "<your_header.h>"
  ],
  "copyright_header": [
    "// Generated test file"
  ]
}
```

## MCP 服务器调试

### 手动启动服务器

```bash
python mcp_server.py
```

服务器将在标准 stdio 上提供 MCP 协议，Claude Code IDE 可以通过 .mcp.json 连接到它。

### 查看可用工具

```bash
# 服务器启动时会打印可用的工具
python mcp_server.py
```

## 故障排除

### 找不到 libclang

确保 LLVM/Clang 已安装，或手动设置 libclang 路径：

```python
import clang.cindex
clang.cindex.conf.set_library_file('/path/to/libclang.dll')  # Windows
# 或
clang.cindex.conf.set_library_file('/path/to/libclang.so')   # Linux
```

### 找不到编译数据库

编译数据库应该在构建目录中生成。对于 CMake 项目：

```bash
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ...
```

### 函数不被识别

确保函数在源文件中有正确的声明，并且编译数据库包含该源文件。

## 体系结构

```
mcp_server.py
├── FastMCP 服务器定义
├── list_functions() - 列出函数工具
├── generate_tests() - 生成测试工具
└── analyze_function() - 分析函数工具

调用链：
Agent → Claude Code → .mcp.json → mcp_server.py → genut 库
                                    ↓
                         ConstraintExtractor
                         CSourceAnalyzer  
                         GTestBuilder
                         StubBuilder
                         (输出测试文件)
```

## 限制

1. 当前仅支持 C 源代码
2. 复杂的宏定义可能无法完全解析
3. 依赖于 compile_commands.json 的准确性

## 扩展

可以在 `mcp_server.py` 中添加更多工具：

```python
@mcp.tool()
def your_new_tool(param: str) -> dict:
    """Your tool description"""
    # Implementation
    return {"result": "..."}
```

## 许可证

与 genut 项目相同
