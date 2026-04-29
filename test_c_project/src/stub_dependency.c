/**
 * @file stub_dependency.c
 * @brief 分支由函数调用结果决定的测试用例
 *
 * 本文件包含两类测试场景：
 * 1. 函数指针分支：通过全局/结构体/参数函数指针的调用结果决定分支路径
 * 2. 直接调用分支：通过直接函数调用的返回值或出参决定分支路径
 *    此类函数必须使用 INSTALL_STUB 才能覆盖全部分支路径
 */

#include "stub_dependency.h"
#include <stdio.h>
#include <string.h>
#include <limits.h>

/*============================================================================
 * Global function pointers
 *===========================================================================*/

int (*global_math_op)(int, int) = NULL;
void (*global_printer)(const char*) = NULL;
int (*global_op_array[4])(int, int) = {NULL, NULL, NULL, NULL};

/*============================================================================
 * Struct with function pointer fields
 *===========================================================================*/

MathOperation global_math_op_struct = {
    .operation = NULL,
    .logger = NULL,
    .id = 0
};

/*============================================================================
 * Basic scenario examples (placed first for clarity)
 *
 * 场景1：全局函数指针 — 测试中直接赋值 global_math_op = stub_fn
 * 场景2：全局结构体含FP字段 — 测试中赋值 global_math_op_struct.operation = stub_fn
 * 场景3：普通函数打桩 — 测试中使用 INSTALL_STUB(dep_query_int, stub_fn)
 *===========================================================================*/

/** 场景1：分支由全局函数指针 global_math_op 是否为 NULL 及其返回值决定。
 *  非NULL路径需将 global_math_op 赋值为返回特定值的桩函数。 */
int basic_global_fp_branch(int a, int b)
{
    if (global_math_op == NULL) {
        return -1;
    }
    int result = global_math_op(a, b);
    if (result > 0) {
        return 1;
    } else if (result == 0) {
        return 0;
    } else {
        return -2;
    }
}

/** 场景2：分支由全局结构体函数指针字段是否为 NULL 及其返回值决定。
 *  非NULL路径需将 global_math_op_struct.operation 赋值为返回特定值的桩函数。 */
int basic_global_struct_fp_branch(int a, int b)
{
    if (global_math_op_struct.operation == NULL) {
        return -1;
    }
    int result = global_math_op_struct.operation(a, b);
    if (result > 0) {
        return 1;
    } else if (result == 0) {
        return 0;
    } else {
        return -2;
    }
}

/** 场景3：分支由直接调用 dep_query_int() 的返回值决定。
 *  必须通过 INSTALL_STUB(dep_query_int, stub_fn) 才能覆盖全部路径。 */
int basic_install_stub_branch(void)
{
    int v = dep_query_int();
    if (v > 0) {
        return 1;
    } else if (v == 0) {
        return 0;
    } else if (v == -1) {
        return -1;
    } else {
        return -2;
    }
}

/** 场景4：分支由两个 dep_* 返回值的关系决定。
 *  a 和 b 均为 call-result 局部变量，生成器将 b 视为 0，仅对 a 生成桩约束。 */
int basic_dual_return_compare(void)
{
    int a = dep_read_sensor_a();
    int b = dep_read_sensor_b();
    if (a > b) {
        return 1;
    } else if (a == b) {
        return 0;
    } else {
        return -1;
    }
}

/** 场景5：出参整数值驱动分支。
 *  dep_load_value 通过 *out_val 写入整数，桩需同时控制返回值（决定错误路径）
 *  和 *out_val（决定正常路径内的具体分支）。 */
int basic_outparam_branch(const char* key)
{
    int val = 0;
    int ret = dep_load_value(key, &val);
    if (ret != 0) {
        return -1;
    }
    if (val > 100) {
        return 2;
    } else if (val > 0) {
        return 1;
    } else {
        return 0;
    }
}

/*============================================================================
 * Functions taking function pointers as parameters
 *===========================================================================*/

int compute_with_op(int (*op)(int, int), int x, int y)
{
    if (op == NULL) {
        return 0;
    }
    return op(x, y);
}

int compute_with_math_op(MathOperation* math_op, int x, int y)
{
    if (math_op == NULL || math_op->operation == NULL) {
        return 0;
    }
    return math_op->operation(x, y);
}

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

int (*get_operation(char op))(int, int)
{
    switch (op) {
        case '+': return add;
        case '-': return sub;
        case '*': return mul;
        case '/': return div_safe;
        default:  return NULL;
    }
}

int (*get_operation_by_index(int index))(int, int)
{
    if (index < 0 || index >= 4) {
        return NULL;
    }
    return global_op_array[index];
}

/*============================================================================
 * Complex test functions: function-pointer-driven branches
 *===========================================================================*/

int test_global_func_ptr_calls(int a, int b)
{
    int result1 = 0;
    int result2 = 0;

    if (global_math_op != NULL) {
        result1 = global_math_op(a, b);
    }
    if (global_op_array[2] != NULL) {
        result2 = global_op_array[2](a, b);
    }
    if (global_printer != NULL) {
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "Results: %d, %d", result1, result2);
        global_printer(buffer);
    }

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
        return -1;
    }

    if (result > 100) {
        return 100;
    } else if (result > 50) {
        return result;
    } else {
        return 0;
    }
}

int test_struct_func_ptr(MathOperation* op, int x, int y)
{
    if (op == NULL) {
        return -1;
    }

    int result = 0;

    if (op->operation != NULL) {
        result = op->operation(x, y);
    }
    if (op->logger != NULL) {
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "Struct operation result: %d", result);
        op->logger(buffer);
    }

    if (result > 1000) {
        return 1000;
    } else if (result > 100) {
        return result;
    } else {
        return 0;
    }
}

int test_returned_func_ptr(char op, int x, int y)
{
    int (*fp)(int, int) = get_operation(op);

    if (fp == NULL) {
        return -1;
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

int test_mixed_func_ptr_sources(int a, int b, char op_char, MathOperation* math_op)
{
    int total = 0;

    if (global_math_op != NULL) {
        total += global_math_op(a, b);
    }
    if (math_op != NULL && math_op->operation != NULL) {
        total += math_op->operation(a, b);
    }
    int (*op_from_return)(int, int) = get_operation(op_char);
    if (op_from_return != NULL) {
        total += op_from_return(a, b);
    }
    if (global_op_array[2] != NULL) {
        total += global_op_array[2](a, b);
    }

    if (total > 1000) {
        return 1000;
    } else if (total > 0) {
        return total;
    } else {
        return 0;
    }
}

int test_nested_func_ptr_calls(int a, int b)
{
    int (*fp)(int, int) = get_operation('+');
    if (fp == NULL) {
        return -1;
    }

    int result1 = fp(a, b);
    int (*fp2)(int, int) = get_operation('-');

    if (global_printer != NULL) {
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "Nested call intermediate: %d", result1);
        global_printer(buffer);
    }

    if (fp2 == NULL) {
        return result1;
    }

    int result2 = fp2(a, b);

    if (result2 > 100) {
        return 100;
    } else {
        return result2;
    }
}

int test_func_ptr_in_condition(int a, int b, int (*op1)(int, int), int (*op2)(int, int))
{
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

/*============================================================================
 * Functions under test: branches driven by direct call results
 * 以下函数展示 UT 生成场景：分支完全由直接函数调用结果决定，
 * 无法通过参数或全局函数指针控制，必须 INSTALL_STUB 才能覆盖全部路径。
 *===========================================================================*/

/**
 * @brief 单依赖返回值分支：4 条路径
 *
 * 分支由 dep_query_int() 返回值决定，无参数可控制走向。
 * 演示场景：单个直接调用的返回值驱动多路分支。
 *
 * @return 1/2/3=各分支处理结果, 0=兜底路径
 */
int branch_on_retval(void)
{
    int code = dep_query_int();

    if (code == 0) {
        return 1;
    } else if (code == 1) {
        return 2;
    } else if (code == 2) {
        return 3;
    } else {
        return 0;
    }
}

/**
 * @brief 出参驱动分支：4 条路径
 *
 * 分支由 dep_fill_buf() 返回值决定。
 * 演示场景：依赖函数通过出参传递数据，返回值决定分支。
 *
 * @param key 查询键
 * @return >=0=buf内容长度, -1/-2/-3=各错误路径
 */
int branch_on_outparam(const char* key)
{
    char buf[64];
    int ret = dep_fill_buf(key, buf, sizeof(buf));

    if (ret == -1) {
        return -1;
    } else if (ret == -2) {
        return -2;
    } else if (ret != 0) {
        return -3;
    }

    return (int)strlen(buf);
}

/**
 * @brief 双依赖联合分支：5 条路径
 *
 * 分支由 dep_read_sensor_a() 和 dep_read_sensor_b() 共同决定。
 * 演示场景：两个直接调用的返回值联合决定复合条件分支。
 *
 * @param limit_a  sensor_a 上限
 * @param min_b    sensor_b 下限
 * @return  2=均满足,  1=仅 a 满足,
 *         -1=仅 b 满足, -2=均不满足, -3=读取失败(INT_MIN)
 */
int branch_on_dual_calls(int limit_a, int min_b)
{
    int a = dep_read_sensor_a();
    int b = dep_read_sensor_b();

    if (a == INT_MIN || b == INT_MIN) {
        return -3;
    }

    if (a <= limit_a && b >= min_b) {
        return 2;
    } else if (a <= limit_a) {
        return 1;
    } else if (b >= min_b) {
        return -1;
    } else {
        return -2;
    }
}

/**
 * @brief 配对调用分支：4 条路径
 *
 * 分支由 dep_acquire() 返回值决定；成功路径额外调用 dep_release()。
 * 演示场景：acquire/release 配对调用，acquire 失败时不走 release。
 *
 * @param name  资源名
 * @param value 待处理值
 * @return value*2=成功, -1/-2/-3=各错误路径
 */
int branch_with_paired_calls(const char* name, int value)
{
    int ret = dep_acquire(name);

    if (ret == -1) {
        return -1;
    } else if (ret == -2) {
        return -2;
    } else if (ret != 0) {
        return -3;
    }

    int result = value * 2;
    dep_release(name);
    return result;
}
