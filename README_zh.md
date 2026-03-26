# genut: C 语言单元测试生成器

一个基于 libclang 的 Python 工具，用于解析 C 源文件并生成 Google Test (GTest) 单元测试骨架。它能提取函数签名、计算圈复杂度、识别分支路径（if/else、switch/case），并生成带参数约束的测试用例。

## 特性

- **基于 AST 的分析**：使用 libclang 解析 C 源代码，获取完整的类型信息
- **路径约束提取**：自动从 if/switch 分支条件中提取参数约束
- **可配置架构**：项目特定定制化功能（命名、默认值、编译器）与核心逻辑解耦
- **编译数据库支持**：使用 `compile_commands.json` 获取准确的编译参数
- **圈复杂度计算**：根据函数复杂度生成适当数量的测试用例
- **模块化设计**：关注点分离，支持配置注入

## 快速开始

### 1. 安装依赖

```bash
pip install libclang
```

### 2. 准备编译数据库

确保你的 C 项目有 `compile_commands.json` 文件：

```bash
# 对于 CMake 项目
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..

# 对于 Make 项目（使用 Bear）
bear -- make
```

### 3. 生成单元测试

```bash
# 为源文件生成测试
python gen_ut.py --compdb compile_commands.json --src src/math_utils.c

# 使用自定义配置
python gen_ut.py --config utgen.json --compdb compile_commands.json --src src/math_utils.c
```

### 4. 编译和运行测试

```bash
# 使用 GTest 编译
g++ -std=c++11 -I. -I/path/to/gtest/include ut_math_utils.cpp \
    -L/path/to/gtest/lib -lgtest -lgtest_main -o math_utils_test

# 运行测试
./math_utils_test
```

## 架构

该工具经过重构，采用模块化架构，明确分离了通用 UT 生成功能和项目特定定制化功能：

```plain
genut/
├── gen_ut.py           # 主入口脚本
├── config.py           # 配置类（GeneratorConfig、NamingConfig、DefaultValueConfig）
├── models.py           # 数据模型（PathConstraint、FunctionInfo）
├── compdb.py           # 编译数据库解析器，支持编译器自动检测
├── analyzer.py         # C 源代码分析器（使用 libclang）
├── extractor.py        # 函数 AST 约束提取器
├── builder.py          # GTest 构建器，支持可配置命名和默认值
├── CLAUDE.md           # Claude Code 项目说明
└── test_c_project/     # 测试用的示例 C 项目
```

### 核心组件

| 组件 | 职责 |
| ------ | ------ |
| **CompDbParser** | 解析 `compile_commands.json`，提取编译参数，支持编译器自动检测 |
| **CSourceAnalyzer** | 使用 libclang 解析 C 源代码，提取函数信息 |
| **ConstraintExtractor** | 提取 if/switch 分支条件，生成路径约束 |
| **GTestBuilder** | 生成 GTest 兼容的 `.cpp` 和 `.h` 文件，支持可配置命名和默认值 |
| **UTGeneratorApp** | 主入口点，处理 CLI 参数 |

## 安装

### 系统要求

- Python 3.7+
- LLVM/Clang 安装，包含 libclang DLL/库文件
- Python 包：`clang`（libclang Python 绑定）

```bash
pip install clang
```

### 系统特定安装

- **Windows**：从 [llvm.org](https://llvm.org/) 安装 LLVM 或使用 Chocolatey：`choco install llvm`
- **Linux**：使用包管理器安装：`sudo apt-get install clang libclang-dev`
- **macOS**：使用 Homebrew 安装：`brew install llvm`

确保 libclang 库路径在系统 PATH 中，或设置 `LIBCLANG_PATH` 环境变量。

## 使用方法

### 基本用法

```bash
# 为 C 源文件生成测试
python gen_ut.py --compdb <compile_commands.json> --src <source_file.c>

# 从分支条件构造参数
python gen_ut.py --compdb compile_commands.json --src src/file.c --construct

# 输出到指定目录
python gen_ut.py --compdb compile_commands.json --src src/file.c --outdir test/

# 仅针对特定函数
python gen_ut.py --compdb compile_commands.json --src src/file.c --funcs "func1;func2"

# 指定项目根目录以便正确识别内部头文件
python gen_ut.py --compdb compile_commands.json --src src/file.c --project-root /path/to/project
```

### 命令行选项

| 选项 | 描述 |
| ------ | ------ |
| `--compdb` | `compile_commands.json` 文件路径（必需） |
| `--src` | C 源文件路径（必需） |
| `--funcs` | 目标函数列表，分号分隔。留空表示所有函数。 |
| `--outdir` | 生成文件的输出目录。默认为源文件所在目录。 |
| `--construct` | 从分支条件构造测试参数。 |
| `--project-root` | 显式指定项目根目录，以便正确识别内部头文件。 |
| `--config, -c` | JSON 配置文件路径，用于自定义命名、默认值等。 |
| `--compiler` | 用于系统包含路径检测的编译器（auto、gcc 或 clang）。 |

## 配置

该工具支持 JSON 配置文件，可为不同项目自定义行为。可自定义的内容包括：

- **命名约定**：文件前缀/后缀、测试套件后缀、测试名称模式
- **默认值**：类型特定的默认值（int、float、指针、结构体、自定义类型）
- **编译器选择**：自动或显式编译器检测，用于系统包含路径
- **类型识别**：可扩展的基本类型关键字列表

### 配置文件示例

创建 `utgen.json`：

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

### 使用配置

```bash
python gen_ut.py --config utgen.json --compdb compile_commands.json --src src/file.c
```

## 工作原理

### 1. 编译数据库解析

- 读取 `compile_commands.json` 提取编译参数
- 自动检测编译器（gcc/clang）或使用显式配置
- 从检测到的编译器添加系统包含路径

### 2. 源代码分析

- 使用 libclang 将 C 源文件解析为 AST
- 提取带参数类型的函数声明
- 计算每个函数的圈复杂度
- 识别全局变量依赖

### 3. 约束提取

- 遍历函数 AST 查找 if/switch 语句
- 提取分支条件和参数约束
- 为每个可能的执行路径生成路径约束
- 处理嵌套条件和逻辑运算符

### 4. 测试生成

- 创建包含 `extern "C"` 函数声明的头文件
- 为每个路径约束生成 GTest 测试用例
- 使用配置进行命名约定和默认值设置
- 可选地从分支条件构造测试参数

### 输出文件

使用默认配置：

- `ut_<模块>.h` - 包含 `extern "C"` 函数声明的头文件
- `ut_<模块>.cpp` - GTest 测试用例

使用自定义配置（`file_prefix: "test_"`，`suite_suffix: "UT"`）：

- `test_<模块>.h` - 包含 `extern "C"` 函数声明的头文件
- `test_<模块>.cpp` - GTest 测试用例，使用 `MathUtilsUT` 测试套件类

## 测试项目

`test_c_project/` 目录包含一个用于测试生成器的示例 C 项目。

### 构建测试项目

**Windows (PowerShell):**

```bash
cd test_c_project
.\build.ps1          # 构建
.\build.ps1 clean   # 清理
```

**Unix/Git Bash:**

```bash
cd test_c_project
./build.sh          # 构建
./build.sh clean    # 清理
```

构建输出：

- 二进制文件：`build/test_c_project.exe`
- 编译数据库：`compile_commands.json`（libclang 使用）

### 为测试项目生成测试

```bash
# 默认配置
python gen_ut.py --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c --outdir test_c_project/test

# 自定义配置
python gen_ut.py --config utgen.json --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c  --outdir test_c_project/test

# 使用参数构造
python gen_ut.py --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c  --outdir test_c_project/test --construct
```

## 扩展和定制

### 添加自定义类型默认值

在配置中添加项目特定类型：

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

### 自定义命名模式

调整命名模式以匹配项目约定：

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

### 扩展基本类型识别

添加项目特定类型关键字：

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

## 限制

1. **仅支持 C 语言**：当前仅支持 C 源文件（不支持 C++）
2. **简单约束求解**：约束提取处理基本比较但不支持复杂表达式
3. **局部变量引用**：无法自动解析返回表达式中的局部变量引用
4. **函数指针**：对函数指针类型的支持有限
5. **复杂宏**：预处理器宏在解析期间展开，可能影响分支检测

## 故障排除

### 常见问题

**"libclang not found" 错误：**

```bash
# 设置 libclang 库路径
export LIBCLANG_PATH="/path/to/libclang.so"
# 或在 Windows 上
set LIBCLANG_PATH=C:\path\to\libclang.dll
```

**缺少编译数据库：**

- 确保你的构建系统生成 `compile_commands.json`
- 对于 CMake：`cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..`
- 对于 Make 项目：使用 Bear（`bear -- make`）

**包含路径不正确：**

- 使用 `--project-root` 指定项目根目录
- 检查 `compile_commands.json` 是否包含正确路径

## 贡献

1. Fork 仓库
2. 创建特性分支
3. 进行更改并添加适当的测试
4. 提交 Pull Request

### 开发环境设置

```bash
git clone <仓库地址>
cd genut
pip install -r requirements.txt  # 如果存在 requirements.txt 文件
```

### 运行测试

```bash
# 运行集成测试
python -m pytest test/  # 如果存在 test 目录

# 使用示例项目测试
cd test_c_project
./build.sh
cd ..
python gen_ut.py --compdb test_c_project/compile_commands.json --src test_c_project/src/math_utils.c
```

## 许可证

[MIT 许可证](LICENSE)

## 致谢

- 基于 [libclang](https://clang.llvm.org/docs/Tooling.html) 进行 C/C++ 解析
- 为 [Google Test](https://github.com/google/googletest) 框架生成测试
- 受各种单元测试生成工具和研究的启发
