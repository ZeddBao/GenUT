#ifndef STUB_TEST_H
#define STUB_TEST_H

#include <stdint.h>
#include <stdbool.h>

/* 用于打桩测试的结构体 */
typedef struct {
    int32_t value;
    int32_t threshold;
    bool enabled;
} ConfigData;

typedef struct {
    int32_t x;
    int32_t y;
    int32_t result;
} PointData;

/* 将被打桩的函数声明（模拟外部依赖） */

/**
 * 获取配置值的函数 - 基于返回值进行分支
 */
ConfigData get_configuration(void);

/**
 * 验证输入的函数 - 返回验证结果
 */
int32_t validate_input(int32_t input);

/**
 * 处理数据的函数 - 通过指针参数返回结果
 */
void process_data(int32_t input, int32_t* output);

/**
 * 计算结果的函数 - 返回计算值
 */
int32_t calculate_result(int32_t a, int32_t b);

/**
 * 检查状态的函数 - 返回布尔状态
 */
bool check_system_status(void);

/**
 * 更新配置的函数 - 通过结构体指针返回更新后的配置
 */
void update_config(ConfigData* config);

/**
 * 获取点数据的函数 - 返回结构体
 */
PointData get_point_data(void);

/**
 * 复杂计算的函数 - 多个参数和返回值
 */
int32_t complex_calculation(int32_t a, int32_t b, int32_t c);

/* 测试函数声明 */

/**
 * 测试1: 分支条件直接依赖于函数返回值
 * 根据validate_input()的返回值决定分支
 */
int32_t test_branch_on_return_value(int32_t input);

/**
 * 测试2: 分支条件依赖于指针参数修改的值
 * process_data()通过output参数返回值，分支基于此值
 */
int32_t test_branch_on_output_param(int32_t input);

/**
 * 测试3: 多层嵌套的函数调用条件
 * 多个函数调用结果的组合条件
 */
int32_t test_nested_function_conditions(int32_t a, int32_t b);

/**
 * 测试4: 结构体返回值的字段条件
 * 根据get_configuration()返回的结构体字段进行分支
 */
int32_t test_struct_return_field_condition(void);

/**
 * 测试5: 布尔返回值的条件
 * 根据check_system_status()的布尔返回值分支
 */
int32_t test_boolean_return_condition(void);

/**
 * 测试6: 通过指针参数修改结构体的条件
 * update_config()修改config参数，分支基于修改后的字段
 */
int32_t test_pointer_param_struct_condition(ConfigData* config);

/**
 * 测试7: 多个函数调用的逻辑组合
 * 使用逻辑运算符连接多个函数调用结果
 */
int32_t test_multi_function_logic(void);

/**
 * 测试8: 函数调用在循环中的条件
 * 循环内调用函数，根据返回值决定循环行为
 */
int32_t test_function_in_loop(int32_t* array, int32_t size);

/**
 * 测试9: 函数调用在switch语句中的条件
 * switch基于函数返回值
 */
int32_t test_function_in_switch(int32_t input);

/**
 * 测试10: 复杂表达式中的函数调用
 * 函数调用作为复杂表达式的一部分
 */
int32_t test_function_in_complex_expression(int32_t a, int32_t b, int32_t c);

#endif // STUB_TEST_H