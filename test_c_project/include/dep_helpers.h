/**
 * @file dep_helpers.h
 * @brief 辅助函数声明
 *
 * 包含三类辅助函数：
 * 1. 基本运算函数（add/sub/mul/div_safe/print_message）：作为函数指针目标被间接调用
 * 2. 内存分配辅助（malloc_test/null_pointer_return）：模拟分配成功/失败场景
 * 3. 依赖桩函数（dep_*）：被 stub_dependency.c 中的被测函数直接调用，
 *    测试时通过 INSTALL_STUB 替换以覆盖全部分支路径
 */

#ifndef DEP_HELPERS_H
#define DEP_HELPERS_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/*============================================================================
 * Basic functions (used as function pointer targets)
 *===========================================================================*/

int add(int a, int b);
int sub(int a, int b);
int mul(int a, int b);
int div_safe(int a, int b);
void print_message(const char* msg);

/*============================================================================
 * Memory allocation helpers
 * 模拟分配成功/失败场景，合并自 basic_functions、error_handling、memory_management
 *===========================================================================*/

/** 分配 size 字节；size==0 或 >1GB 时返回 NULL，模拟大内存分配失败。 */
void* malloc_test(size_t size);

/** 分配 size 字节；size==0 或 >1MB 时返回 NULL，模拟严格限制场景。 */
void* null_pointer_return(size_t size);

/*============================================================================
 * Stub dependency functions (direct calls, not function pointers)
 * 以下函数被 stub_dependency.c 中的被测函数直接调用，其返回值或出参决定分支走向。
 * 默认实现返回固定值，测试时必须通过 INSTALL_STUB 替换才能覆盖全部分支路径。
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

#ifdef __cplusplus
}
#endif

#endif /* DEP_HELPERS_H */
