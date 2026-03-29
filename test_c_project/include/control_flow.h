/**
 * @file control_flow.h
 * @brief 控制流测试 - 演示各种控制流场景，用于单元测试生成
 *
 * 本头文件包含控制流测试的示例函数声明，涵盖：
 * 1. 条件分支覆盖：if/else、switch、三元运算符
 * 2. 循环覆盖：for、while、do-while、嵌套循环、break/continue
 * 3. 复杂逻辑表达式：逻辑运算符、比较运算符、算术运算、位运算
 */

#ifndef CONTROL_FLOW_H
#define CONTROL_FLOW_H

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ==================== 2.1 条件分支覆盖 ==================== */

/* ----- if/else语句 ----- */

/**
 * @brief 简单if/else语句测试
 * @param value 输入值
 * @return 根据条件返回不同的值
 */
int simple_if_else(int value);

/**
 * @brief 嵌套if语句测试
 * @param a 第一个参数
 * @param b 第二个参数
 * @param c 第三个参数
 * @return 多层条件组合的结果
 */
int nested_if_statements(int a, int b, int c);

/**
 * @brief 多重if-else if-else链测试
 * @param score 分数
 * @return 分数等级
 */
int if_else_if_chain(int score);

/* ----- switch语句 ----- */

/**
 * @brief switch语句测试，包含多个case和default
 * @param command 命令代码
 * @return 命令执行结果
 */
int switch_statement_test(int command);

/**
 * @brief switch语句测试，带fall-through情况
 * @param month 月份
 * @return 该月的天数
 */
int switch_with_fallthrough(int month);

/* ----- 三元运算符 ----- */

/**
 * @brief 三元运算符测试
 * @param a 第一个值
 * @param b 第二个值
 * @return 较大的值
 */
int ternary_operator_test(int a, int b);

/**
 * @brief 嵌套三元运算符测试
 * @param a 第一个值
 * @param b 第二个值
 * @param c 第三个值
 * @return 三个值中的最大值
 */
int nested_ternary_operator(int a, int b, int c);

/* ==================== 2.2 循环覆盖 ==================== */

/* ----- for循环 ----- */

/**
 * @brief for循环测试：零次、一次、多次迭代
 * @param n 循环次数
 * @return 循环累加结果
 */
int for_loop_test(int n);

/**
 * @brief for循环测试，包含多个控制变量
 * @param rows 行数
 * @param cols 列数
 * @return 总元素数
 */
int for_loop_multiple_variables(int rows, int cols);

/* ----- while循环 ----- */

/**
 * @brief while循环测试：条件边界测试
 * @param target 目标值
 * @return 达到目标所需的迭代次数
 */
int while_loop_test(int target);

/**
 * @brief while循环测试，包含复杂条件
 * @param data 数据数组
 * @param size 数组大小
 * @return 满足条件的数据个数
 */
int while_loop_complex_condition(const int* data, int size);

/* ----- do-while循环 ----- */

/**
 * @brief do-while循环测试：至少执行一次的场景
 * @param initial 初始值
 * @param limit 限制值
 * @return 最终值
 */
int do_while_loop_test(int initial, int limit);

/* ----- 嵌套循环 ----- */

/**
 * @brief 嵌套循环测试：两层循环
 * @param rows 行数
 * @param cols 列数
 * @return 二维索引之和
 */
int nested_loops_test(int rows, int cols);

/**
 * @brief 三层嵌套循环测试
 * @param a 第一维大小
 * @param b 第二维大小
 * @param c 第三维大小
 * @return 三维索引之积的和
 */
int three_level_nested_loops(int a, int b, int c);

/* ----- break/continue语句 ----- */

/**
 * @brief break语句测试：提前退出循环
 * @param data 数据数组
 * @param size 数组大小
 * @param search_value 要查找的值
 * @return 找到的索引，未找到返回-1
 */
int break_statement_test(const int* data, int size, int search_value);

/**
 * @brief continue语句测试：跳过某些迭代
 * @param n 循环次数
 * @return 跳过奇数后的偶数之和
 */
int continue_statement_test(int n);

/* ==================== 2.3 复杂逻辑表达式 ==================== */

/* ----- 逻辑运算符 ----- */

/**
 * @brief 逻辑与(&&)运算符测试
 * @param a 第一个条件
 * @param b 第二个条件
 * @return 条件组合结果
 */
int logical_and_test(int a, int b);

/**
 * @brief 逻辑或(||)运算符测试
 * @param a 第一个条件
 * @param b 第二个条件
 * @return 条件组合结果
 */
int logical_or_test(int a, int b);

/**
 * @brief 逻辑非(!)运算符测试
 * @param a 条件值
 * @return 逻辑非结果
 */
int logical_not_test(int a);

/**
 * @brief 混合逻辑表达式测试
 * @param a 第一个值
 * @param b 第二个值
 * @param c 第三个值
 * @return 复杂逻辑表达式的结果
 */
int complex_logical_expression(int a, int b, int c);

/* ----- 比较运算符 ----- */

/**
 * @brief 比较运算符测试：==, !=, <, >, <=, >=
 * @param x 第一个值
 * @param y 第二个值
 * @return 比较结果编码
 */
int comparison_operators_test(int x, int y);

/* ----- 算术运算在条件中 ----- */

/**
 * @brief 算术运算在条件中测试：+, -, *, /, %
 * @param a 第一个操作数
 * @param b 第二个操作数
 * @return 基于算术运算条件的结果
 */
int arithmetic_in_condition(int a, int b);

/**
 * @brief 除法在条件中测试，注意除零保护
 * @param a 被除数
 * @param b 除数
 * @return 基于除法结果的条件返回值
 */
int division_in_condition(int a, int b);

/* ----- 位运算在条件中 ----- */

/**
 * @brief 位运算在条件中测试：&, |, ^, ~, <<, >>
 * @param flags 标志位
 * @param mask 掩码
 * @return 基于位运算条件的结果
 */
int bitwise_in_condition(int flags, int mask);

#ifdef __cplusplus
}
#endif

#endif /* CONTROL_FLOW_H */