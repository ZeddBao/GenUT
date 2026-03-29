/**
 * @file func_ptr_test.c
 * @brief 函数指针测试 - 实现各种函数指针使用场景，用于单元测试生成
 *
 * 本文件实现函数指针测试的示例函数，涵盖：
 * 1. 基础函数：用于函数指针调用的简单函数
 * 2. 全局函数指针变量：全局定义的函数指针
 * 3. 包含函数指针的结构体：结构体中的函数指针字段
 * 4. 函数指针参数：函数接收函数指针作为参数
 * 5. 返回函数指针的函数：函数返回函数指针
 * 6. 复杂测试函数：各种函数指针使用场景的集成测试
 */

#include "func_ptr_test.h"
#include <stdio.h>
#include <string.h>

/*============================================================================
 * Basic functions
 *===========================================================================*/

/**
 * @brief 加法函数
 * @param a 第一个加数
 * @param b 第二个加数
 * @return 两个参数的和
 */
int add(int a, int b)
{
    return a + b;
}

/**
 * @brief 减法函数
 * @param a 被减数
 * @param b 减数
 * @return 两个参数的差
 */
int sub(int a, int b)
{
    return a - b;
}

/**
 * @brief 乘法函数
 * @param a 第一个乘数
 * @param b 第二个乘数
 * @return 两个参数的乘积
 */
int mul(int a, int b)
{
    return a * b;
}

/**
 * @brief 安全除法函数
 * @param a 被除数
 * @param b 除数
 * @return 两个参数的商，如果除数为0则返回0
 */
int div_safe(int a, int b)
{
    if (b == 0) {
        return 0; // 避免除零
    }
    return a / b;
}

/**
 * @brief 打印消息函数
 * @param msg 要打印的消息
 */
void print_message(const char* msg)
{
    if (msg != NULL) {
        printf("Message: %s\n", msg);
    }
}

/*============================================================================
 * Global function pointers
 *===========================================================================*/

// 全局函数指针变量定义
int (*global_math_op)(int, int) = NULL;
void (*global_printer)(const char*) = NULL;
int (*global_op_array[4])(int, int) = {NULL, NULL, NULL, NULL};

/*============================================================================
 * Struct with function pointer fields
 *===========================================================================*/

// 全局函数指针结构体定义
MathOperation global_math_op_struct = {
    .operation = NULL,
    .logger = NULL,
    .id = 0
};

/*============================================================================
 * Functions taking function pointers as parameters
 *===========================================================================*/

/**
 * @brief 使用函数指针进行计算
 * @param op 函数指针，指向接收两个int参数并返回int的函数
 * @param x 第一个操作数
 * @param y 第二个操作数
 * @return 函数指针调用的结果，如果指针为NULL则返回0
 */
int compute_with_op(int (*op)(int, int), int x, int y)
{
    if (op == NULL) {
        return 0;
    }
    return op(x, y);
}

/**
 * @brief 使用MathOperation结构体中的函数指针进行计算
 * @param math_op MathOperation结构体指针
 * @param x 第一个操作数
 * @param y 第二个操作数
 * @return 函数指针调用的结果，如果结构体或函数指针为NULL则返回0
 */
int compute_with_math_op(MathOperation* math_op, int x, int y)
{
    if (math_op == NULL || math_op->operation == NULL) {
        return 0;
    }
    return math_op->operation(x, y);
}

/**
 * @brief 使用回调函数处理数据
 * @param value 要处理的值
 * @param callback 回调函数指针，指向接收const char*参数并返回void的函数
 */
void process_with_callback(int value, void (*callback)(const char*))
{
    char buffer[32];
    snprintf(buffer, sizeof(buffer), "Processed: %d", value);

    if (callback != NULL) {
        callback(buffer);
    }
}

/*============================================================================
 * Functions returning function pointers
 *===========================================================================*/

/**
 * @brief 根据操作符返回对应的函数指针
 * @param op 操作符：'+', '-', '*', '/'
 * @return 指向对应数学运算函数的指针，如果操作符无效则返回NULL
 */
int (*get_operation(char op))(int, int)
{
    switch (op) {
        case '+':
            return add;
        case '-':
            return sub;
        case '*':
            return mul;
        case '/':
            return div_safe;
        default:
            return NULL;
    }
}

/**
 * @brief 根据索引返回全局函数指针数组中的元素
 * @param index 索引值 (0-3)
 * @return 对应索引的函数指针，如果索引越界则返回NULL
 */
int (*get_operation_by_index(int index))(int, int)
{
    if (index < 0 || index >= 4) {
        return NULL;
    }
    return global_op_array[index];
}

/*============================================================================
 * Complex test functions
 *===========================================================================*/

/**
 * @brief 测试全局函数指针调用
 * @param a 第一个参数
 * @param b 第二个参数
 * @return 根据各种条件组合的计算结果
 */
int test_global_func_ptr_calls(int a, int b)
{
    int result1 = 0;
    int result2 = 0;

    // 使用全局函数指针
    if (global_math_op != NULL) {
        result1 = global_math_op(a, b);
    }

    // 使用全局函数指针数组（索引2）
    if (global_op_array[2] != NULL) {
        result2 = global_op_array[2](a, b);
    }

    // 如果global_printer可用，打印结果
    if (global_printer != NULL) {
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "Results: %d, %d", result1, result2);
        global_printer(buffer);
    }

    // 根据结果组合返回不同的值
    if (result1 > result2) {
        return result1;
    } else if (result1 > 0 && result2 > 0) {
        return result1 + result2;
    } else if (result1 > 0) {
        return result1;
    } else if (result2 > 0) {
        return result2;
    } else {
        return 0;
    }
}

/**
 * @brief 测试函数指针参数
 * @param op 函数指针参数
 * @param x 第一个操作数
 * @param y 第二个操作数
 * @return 根据各种条件组合的计算结果
 */
int test_func_ptr_param(int (*op)(int, int), int x, int y)
{
    int result = 0;

    if (op != NULL) {
        result = op(x, y);

        if (global_printer != NULL) {
            char buffer[64];
            snprintf(buffer, sizeof(buffer), "Operation result: %d", result);
            global_printer(buffer);
        }
    } else {
        return -1; // 无效函数指针
    }

    if (result > 100) {
        return 100; // 限制最大值
    } else if (result > 50) {
        return result;
    } else {
        return 0;
    }
}

/**
 * @brief 测试结构体中的函数指针
 * @param op 包含函数指针的结构体
 * @param x 第一个操作数
 * @param y 第二个操作数
 * @return 根据各种条件组合的计算结果
 */
int test_struct_func_ptr(MathOperation* op, int x, int y)
{
    if (op == NULL) {
        return -1; // 无效结构体指针
    }

    int result = 0;

    // 使用结构体中的operation函数指针
    if (op->operation != NULL) {
        result = op->operation(x, y);
    }

    // 如果logger可用，记录结果
    if (op->logger != NULL) {
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "Struct operation result: %d", result);
        op->logger(buffer);
    }

    if (result > 1000) {
        return 1000; // 限制最大值
    } else if (result > 100) {
        return result;
    } else {
        return 0;
    }
}

/**
 * @brief 测试返回的函数指针
 * @param op 操作符字符
 * @param x 第一个操作数
 * @param y 第二个操作数
 * @return 根据各种条件组合的计算结果
 */
int test_returned_func_ptr(char op, int x, int y)
{
    // 获取函数指针
    int (*fp)(int, int) = get_operation(op);

    if (fp == NULL) {
        return -1; // 无效操作符
    }

    int result = fp(x, y);

    if (result > 0) {
        return result;
    } else if (result == 0) {
        return 0;
    } else {
        return -1;
    }
}

/**
 * @brief 测试混合函数指针来源
 * @param a 第一个参数
 * @param b 第二个参数
 * @param op_char 操作符字符
 * @param math_op MathOperation结构体指针
 * @return 根据各种条件组合的计算结果
 */
int test_mixed_func_ptr_sources(int a, int b, char op_char, MathOperation* math_op)
{
    int total = 0;

    // 来源1：全局函数指针
    if (global_math_op != NULL) {
        total += global_math_op(a, b);
    }

    // 来源2：结构体中的函数指针
    if (math_op != NULL && math_op->operation != NULL) {
        total += math_op->operation(a, b);
    }

    // 来源3：返回的函数指针
    int (*op_from_return)(int, int) = get_operation(op_char);
    if (op_from_return != NULL) {
        total += op_from_return(a, b);
    }

    // 来源4：全局函数指针数组
    if (global_op_array[2] != NULL) {
        total += global_op_array[2](a, b);
    }

    if (total > 1000) {
        return 1000; // 限制最大值
    } else if (total > 0) {
        return total;
    } else {
        return 0;
    }
}

/**
 * @brief 测试嵌套函数指针调用
 * @param a 第一个参数
 * @param b 第二个参数
 * @return 根据各种条件组合的计算结果
 */
int test_nested_func_ptr_calls(int a, int b)
{
    // 获取第一个函数指针
    int (*fp)(int, int) = get_operation('+');
    if (fp == NULL) {
        return -1;
    }

    int result1 = fp(a, b);

    // 获取第二个函数指针
    int (*fp2)(int, int) = get_operation('-');

    // 如果global_printer可用，打印中间结果
    if (global_printer != NULL) {
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "Nested call intermediate: %d", result1);
        global_printer(buffer);
    }

    if (fp2 == NULL) {
        return result1; // 返回第一个结果
    }

    int result2 = fp2(a, b);

    if (result2 > 100) {
        return 100; // 限制最大值
    } else {
        return result2;
    }
}

/**
 * @brief 测试函数指针在条件表达式中的使用
 * @param a 第一个参数
 * @param b 第二个参数
 * @param op1 第一个函数指针
 * @param op2 第二个函数指针
 * @return 根据各种条件组合的计算结果
 */
int test_func_ptr_in_condition(int a, int b, int (*op1)(int, int), int (*op2)(int, int))
{
    // 检查函数指针是否相等
    if (op1 == op2) {
        return 0;
    }

    int r1 = 0;
    int r2 = 0;

    if (op1 != NULL) {
        r1 = op1(a, b);
    }

    if (op2 != NULL) {
        r2 = op2(a, b);
    }

    if (r1 > r2) {
        return 1;
    } else if (r1 < r2) {
        return -1;
    } else {
        return 0;
    }
}

/**
 * @brief 主测试函数，集成测试各种函数指针场景
 * @return 测试结果汇总
 */
int main_func_ptr_test(void)
{
    int total_score = 0;

    // 测试1：基础函数调用
    total_score += add(10, 20);
    total_score += sub(30, 10);
    total_score += mul(5, 6);
    total_score += div_safe(100, 10);

    // 测试2：设置全局函数指针
    global_math_op = add;
    global_printer = print_message;
    global_op_array[0] = add;
    global_op_array[1] = sub;
    global_op_array[2] = mul;
    global_op_array[3] = div_safe;

    // 测试3：使用全局函数指针
    if (global_math_op != NULL) {
        total_score += global_math_op(5, 3);
    }

    // 测试4：设置结构体函数指针
    global_math_op_struct.operation = add;
    global_math_op_struct.logger = print_message;
    global_math_op_struct.id = 1;

    // 测试5：测试各种复杂函数
    total_score += test_global_func_ptr_calls(10, 5);
    total_score += test_func_ptr_param(add, 8, 4);
    total_score += test_struct_func_ptr(&global_math_op_struct, 6, 3);
    total_score += test_returned_func_ptr('+', 7, 2);
    total_score += test_mixed_func_ptr_sources(4, 2, '*', &global_math_op_struct);
    total_score += test_nested_func_ptr_calls(9, 3);
    total_score += test_func_ptr_in_condition(5, 3, add, sub);

    // 清理
    global_math_op = NULL;
    global_printer = NULL;
    for (int i = 0; i < 4; i++) {
        global_op_array[i] = NULL;
    }

    global_math_op_struct.operation = NULL;
    global_math_op_struct.logger = NULL;
    global_math_op_struct.id = 0;

    return total_score;
}