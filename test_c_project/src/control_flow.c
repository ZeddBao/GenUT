/**
 * @file control_flow.c
 * @brief 控制流测试 - 实现各种控制流场景，用于单元测试生成
 *
 * 本文件实现控制流测试的示例函数，涵盖：
 * 1. 条件分支覆盖：if/else、switch、三元运算符
 * 2. 循环覆盖：for、while、do-while、嵌套循环、break/continue
 * 3. 复杂逻辑表达式：逻辑运算符、比较运算符、算术运算、位运算
 */

#include "control_flow.h"
#include <stddef.h>

/* ==================== 2.1 条件分支覆盖 ==================== */

/* ----- if/else语句 ----- */

int simple_if_else(int value)
{
    if (value > 0) {
        return 1;
    } else if (value < 0) {
        return -1;
    } else {
        return 0;
    }
}

int nested_if_statements(int a, int b, int c)
{
    int result = 0;

    if (a > 0) {
        if (b > 0) {
            result = 1;
        } else {
            result = 2;
        }
    } else {
        if (c > 0) {
            result = 3;
        } else {
            result = 4;
        }
    }

    return result;
}

int if_else_if_chain(int score)
{
    if (score >= 90) {
        return 4; // A
    } else if (score >= 80) {
        return 3; // B
    } else if (score >= 70) {
        return 2; // C
    } else if (score >= 60) {
        return 1; // D
    } else {
        return 0; // F
    }
}

/* ----- switch语句 ----- */

int switch_statement_test(int command)
{
    int result = 0;

    switch (command) {
        case 0:
            result = 100;
            break;
        case 1:
            result = 200;
            break;
        case 2:
            result = 300;
            break;
        case 3:
            result = 400;
            break;
        default:
            result = -1; // 未知命令
            break;
    }

    return result;
}

int switch_with_fallthrough(int month)
{
    int days = 0;

    switch (month) {
        case 1: case 3: case 5: case 7: case 8: case 10: case 12:
            days = 31;
            break;
        case 4: case 6: case 9: case 11:
            days = 30;
            break;
        case 2:
            days = 28; // 简化处理，不考虑闰年
            break;
        default:
            days = -1; // 无效月份
            break;
    }

    return days;
}

/* ----- 三元运算符 ----- */

int ternary_operator_test(int a, int b)
{
    // 使用三元运算符返回较大值
    return (a > b) ? a : b;
}

int nested_ternary_operator(int a, int b, int c)
{
    // 嵌套三元运算符，返回三个值中的最大值
    return (a > b) ? ((a > c) ? a : c) : ((b > c) ? b : c);
}

/* ==================== 2.2 循环覆盖 ==================== */

/* ----- for循环 ----- */

int for_loop_test(int n)
{
    int sum = 0;

    // 测试零次、一次、多次迭代
    for (int i = 0; i < n; i++) {
        sum += i;
    }

    return sum;
}

int for_loop_multiple_variables(int rows, int cols)
{
    int total = 0;

    // 多个控制变量的for循环
    for (int i = 0, j = 0; i < rows && j < cols; i++, j++) {
        total += i * j;
    }

    return total;
}

/* ----- while循环 ----- */

int while_loop_test(int target)
{
    int count = 0;
    int sum = 0;

    // while循环，条件边界测试
    while (sum < target) {
        sum += ++count;
    }

    return count; // 返回需要的迭代次数
}

int while_loop_complex_condition(const int* data, int size)
{
    if (data == NULL || size <= 0) {
        return 0;
    }

    int count = 0;
    int i = 0;

    // while循环，包含复杂条件
    while (i < size && data[i] >= 0 && data[i] <= 100) {
        count++;
        i++;
    }

    return count;
}

/* ----- do-while循环 ----- */

int do_while_loop_test(int initial, int limit)
{
    int value = initial;

    // do-while循环：至少执行一次
    do {
        value *= 2;
    } while (value < limit);

    return value;
}

/* ----- 嵌套循环 ----- */

int nested_loops_test(int rows, int cols)
{
    int total = 0;

    // 两层嵌套循环
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            total += i + j;
        }
    }

    return total;
}

int three_level_nested_loops(int a, int b, int c)
{
    int total = 0;

    // 三层嵌套循环
    for (int i = 0; i < a; i++) {
        for (int j = 0; j < b; j++) {
            for (int k = 0; k < c; k++) {
                total += i * j * k;
            }
        }
    }

    return total;
}

/* ----- break/continue语句 ----- */

int break_statement_test(const int* data, int size, int search_value)
{
    if (data == NULL || size <= 0) {
        return -1;
    }

    int found_index = -1;

    // 使用break提前退出循环
    for (int i = 0; i < size; i++) {
        if (data[i] == search_value) {
            found_index = i;
            break; // 找到后立即退出
        }
    }

    return found_index;
}

int continue_statement_test(int n)
{
    int sum = 0;

    // 使用continue跳过某些迭代
    for (int i = 0; i < n; i++) {
        if (i % 2 != 0) {
            continue; // 跳过奇数
        }
        sum += i; // 只累加偶数
    }

    return sum;
}

/* ==================== 2.3 复杂逻辑表达式 ==================== */

/* ----- 逻辑运算符 ----- */

int logical_and_test(int a, int b)
{
    // 逻辑与运算符
    if (a > 0 && b > 0) {
        return 1;
    } else {
        return 0;
    }
}

int logical_or_test(int a, int b)
{
    // 逻辑或运算符
    if (a > 0 || b > 0) {
        return 1;
    } else {
        return 0;
    }
}

int logical_not_test(int a)
{
    // 逻辑非运算符
    if (!(a > 0)) {
        return 1;
    } else {
        return 0;
    }
}

int complex_logical_expression(int a, int b, int c)
{
    // 混合逻辑表达式
    if ((a > 0 && b < 0) || (c == 0 && a != b)) {
        return 1;
    } else if (!(a == b || b == c) && a > c) {
        return 2;
    } else {
        return 3;
    }
}

/* ----- 比较运算符 ----- */

int comparison_operators_test(int x, int y)
{
    int result = 0;

    if (x == y) result |= 0x01;
    if (x != y) result |= 0x02;
    if (x < y) result |= 0x04;
    if (x > y) result |= 0x08;
    if (x <= y) result |= 0x10;
    if (x >= y) result |= 0x20;

    return result;
}

/* ----- 算术运算在条件中 ----- */

int arithmetic_in_condition(int a, int b)
{
    if (a + b > 100) {
        return 1;
    } else if (a - b < 0) {
        return 2;
    } else if (a * b == 0) {
        return 3;
    } else if (b != 0 && a % b == 0) {
        return 4;
    } else {
        return 5;
    }
}

int division_in_condition(int a, int b)
{
    // 除法在条件中，注意除零保护
    if (b == 0) {
        return -1; // 除零错误
    }

    if (a / b > 10) {
        return 1;
    } else if (a / b < 5) {
        return 2;
    } else {
        return 3;
    }
}

/* ----- 位运算在条件中 ----- */

int bitwise_in_condition(int flags, int mask)
{
    if ((flags & mask) == mask) {
        return 1; // 所有掩码位都设置
    } else if ((flags & mask) != 0) {
        return 2; // 部分掩码位设置
    } else if ((flags | mask) == flags) {
        return 3; // 掩码位是flags的子集
    } else if ((flags ^ mask) == 0) {
        return 4; // flags和mask完全相同
    } else {
        return 0; // 其他情况
    }
}