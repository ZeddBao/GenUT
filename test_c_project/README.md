# Test C Project

这是一个为 `gen_ut.py` 工具设计的测试 C 语言项目，包含多种分支和条件场景。

## 项目结构

```
test_c_project/
├── include/           # 头文件目录
│   ├── math_utils.h
│   ├── data_processor.h
│   └── state_machine.h
├── src/              # 源代码目录
│   ├── math_utils.c
│   ├── data_processor.c
│   ├── state_machine.c
│   └── main.c
├── build/            # 构建输出目录
├── compile_commands.json  # 编译数据库 (libclang 使用)
├── CMakeLists.txt    # CMake 构建脚本
└── README.md         # 本文件
```

## 模块说明

### 1. math_utils.c/h - 数学运算模块

包含多种分支条件场景：

| 函数 | 复杂度 | 分支条件描述 |
|------|--------|--------------|
| `math_calculate` | 高 | switch-case 多分支，每个操作符都是独立分支 |
| `nested_conditions` | 极高 | 三层嵌套 if-else，27种组合 |
| `complex_logic_op` | 中 | 使用 && 和 \|\| 逻辑运算符的复杂条件 |

### 2. data_processor.c/h - 数据处理模块

包含循环条件和计数触发分支的场景：

| 函数 | 复杂度 | 分支条件描述 |
|------|--------|--------------|
| `data_buffer_add` | 中 | 需要添加10个元素后进入激活状态 |
| `data_buffer_process` | 高 | 根据元素数量(>=100, >=50, >=20)进入不同分支 |
| `complex_loop_processor` | 极高 | 内层循环需超过5次才进入特定分支 |
| `bubble_sort` | 中 | 循环提前退出分支 |

### 3. state_machine.c/h - 状态机模块

包含全局变量和函数返回值控制的分支场景：

| 函数 | 复杂度 | 分支条件描述 |
|------|--------|--------------|
| `check_emergency_stop` | 中 | 全局变量(g_system_context)控制分支 |
| `check_temperature_safe` | 高 | 返回多个不同值控制后续分支 |
| `transition_state` | 极高 | switch嵌套 + 函数返回值判断 |
| `state_machine_handle_event` | 高 | 函数返回值 + 全局状态共同决定 |
| `handle_fault` | 高 | 根据错误代码进入不同分支 |

## 使用 gen_ut.py 生成测试

为单个源文件生成测试：

```bash
# 为 math_utils.c 生成测试
python gen_ut.py --compdb compile_commands.json --src src/math_utils.c

# 为 data_processor.c 生成测试
python gen_ut.py --compdb compile_commands.json --src src/data_processor.c

# 为 state_machine.c 生成测试
python gen_ut.py --compdb compile_commands.json --src src/state_machine.c
```

为指定函数生成测试：

```bash
python gen_ut.py --compdb compile_commands.json --src src/math_utils.c --funcs "nested_conditions;complex_logic_op"
```

## 构建项目

使用 CMake 构建：

```bash
cd build
cmake ..
cmake --build .
```

直接使用 gcc 构建：

```bash
gcc -c -Iinclude src/math_utils.c -o build/math_utils.o
gcc -c -Iinclude src/data_processor.c -o build/data_processor.o
gcc -c -Iinclude src/state_machine.c -o build/state_machine.o
gcc -c -Iinclude src/main.c -o build/main.o
gcc build/math_utils.o build/data_processor.o build/state_machine.o build/main.o -o build/test_c_project -lm
```

## 运行程序

```bash
./build/test_c_project
```

## 分支测试场景说明

### 需要打桩/构造参数的场景

1. **函数返回值分支**: `check_temperature_safe()`, `check_emergency_stop()`
   - 返回值决定后续执行路径
   - 需要通过构造参数或修改全局变量来控制返回值

2. **全局变量分支**: `state_machine_handle_event()`, `transition_state()`
   - 依赖 `g_system_context` 全局变量
   - 需要打桩或直接修改全局变量来触发不同分支

3. **循环计数触发分支**: `data_buffer_add()`, `complex_loop_processor()`
   - 需要循环达到特定次数才能进入特定分支
   - `data_buffer_add()` 需要添加 >=10 个元素
   - `complex_loop_processor()` 内层循环需要执行 >5 次

4. **多层嵌套分支**: `nested_conditions()`, `transition_state()`
   - 多层 if-else 或 switch 嵌套
   - 27种组合路径需要完整测试

## 圈复杂度 (Cyclomatic Complexity)

各函数的预计圈复杂度：

| 函数 | 预计复杂度 | 分支数量 |
|------|-----------|----------|
| `math_calculate` | ~8 | 8 (7种操作 + default) |
| `nested_conditions` | ~28 | 27 (3^3组合) + 1 |
| `complex_logic_op` | ~12 | 多个 && \|\| 分支 |
| `data_buffer_add` | ~4 | 4个主要分支 |
| `data_buffer_process` | ~6 | 多个数量阈值分支 |
| `complex_loop_processor` | ~10 | 循环+条件分支 |
| `bubble_sort` | ~4 | 循环+提前退出 |
| `check_emergency_stop` | ~5 | 多个全局条件 |
| `check_temperature_safe` | ~6 | 多个温度区间 |
| `transition_state` | ~20 | 状态机复杂转换 |
| `state_machine_handle_event` | ~12 | 全局+函数返回 |
| `handle_fault` | ~6 | 错误代码分支 |
