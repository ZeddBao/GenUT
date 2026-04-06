/**
 * @file stub_dependency.h
 * @brief 分支由函数调用结果决定的测试用例头文件
 *
 * 本文件包含两类测试场景：
 * 1. 函数指针分支：通过全局/结构体/参数函数指针的调用结果决定分支路径
 * 2. 直接调用分支：通过直接函数调用的返回值或出参决定分支路径
 *    此类函数必须使用 INSTALL_STUB 才能覆盖全部分支路径
 */

#ifndef STUB_DEPENDENCY_H
#define STUB_DEPENDENCY_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*============================================================================
 * Basic functions
 *===========================================================================*/

int add(int a, int b);
int sub(int a, int b);
int mul(int a, int b);
int div_safe(int a, int b);
void print_message(const char* msg);

/*============================================================================
 * Global function pointers
 *===========================================================================*/

extern int (*global_math_op)(int, int);
extern void (*global_printer)(const char*);
extern int (*global_op_array[4])(int, int);

/*============================================================================
 * Struct with function pointer fields
 *===========================================================================*/

typedef struct {
    int (*operation)(int, int);
    void (*logger)(const char*);
    int id;
} MathOperation;

extern MathOperation global_math_op_struct;

/*============================================================================
 * Functions taking function pointers as parameters
 *===========================================================================*/

int compute_with_op(int (*op)(int, int), int x, int y);
int compute_with_math_op(MathOperation* math_op, int x, int y);
void process_with_callback(int value, void (*callback)(const char*));

/*============================================================================
 * Functions returning function pointers
 *===========================================================================*/

int (*get_operation(char op))(int, int);
int (*get_operation_by_index(int index))(int, int);

/*============================================================================
 * Complex test functions: function-pointer-driven branches
 *===========================================================================*/

int test_global_func_ptr_calls(int a, int b);
int test_func_ptr_param(int (*op)(int, int), int x, int y);
int test_struct_func_ptr(MathOperation* op, int x, int y);
int test_returned_func_ptr(char op, int x, int y);
int test_mixed_func_ptr_sources(int a, int b, char op_char, MathOperation* math_op);
int test_nested_func_ptr_calls(int a, int b);
int test_func_ptr_in_condition(int a, int b, int (*op1)(int, int), int (*op2)(int, int));

/*============================================================================
 * Stub dependency functions (direct calls, not function pointers)
 * 以下函数被下方被测函数直接调用，其返回值或出参决定分支走向。
 * 默认实现永远返回固定值，测试时必须通过 INSTALL_STUB（改写跳转地址）
 * 才能覆盖全部分支路径。
 *===========================================================================*/

/** 返回单个整型状态码，默认 0。用于测试：单依赖返回值分支。 */
int dep_query_int(void);

/**
 * 通过出参填充缓冲区，返回状态码，默认成功(0)。
 * 用于测试：出参驱动分支。
 */
int dep_fill_buf(const char* key, char* buf, size_t buf_size);

/** 返回传感器 A 的整型读数，默认 0。用于测试：双依赖联合分支。 */
int dep_read_sensor_a(void);

/** 返回传感器 B 的整型读数，默认 0。用于测试：双依赖联合分支。 */
int dep_read_sensor_b(void);

/**
 * 获取资源锁，返回状态码，默认成功(0)。
 * 用于测试：配对调用（acquire/release）分支。
 */
int dep_acquire(const char* name);

/** 释放资源锁，无返回值。配合 dep_acquire 使用。 */
void dep_release(const char* name);

/*============================================================================
 * Functions under test: branches driven by direct call results
 * 以下函数展示 UT 生成场景：分支完全由直接函数调用结果决定，
 * 无法通过参数或全局函数指针控制，必须 INSTALL_STUB 才能覆盖全部路径。
 *===========================================================================*/

/** 单依赖返回值分支：4 条路径，由 dep_query_int() 返回值决定。 */
int branch_on_retval(void);

/** 出参驱动分支：4 条路径，由 dep_fill_buf() 返回值决定。 */
int branch_on_outparam(const char* key);

/**
 * 双依赖联合分支：5 条路径，由 dep_read_sensor_a() 和
 * dep_read_sensor_b() 的返回值共同决定。
 */
int branch_on_dual_calls(int limit_a, int min_b);

/**
 * 配对调用分支：4 条路径，由 dep_acquire() 返回值决定，
 * 成功路径还需调用 dep_release()。
 */
int branch_with_paired_calls(const char* name, int value);

#ifdef __cplusplus
}
#endif

#endif /* STUB_DEPENDENCY_H */
