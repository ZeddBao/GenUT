/**
 * @file dep_helpers.c
 * @brief 辅助函数实现
 *
 * 包含两类辅助函数：
 * 1. 基本运算函数（add/sub/mul/div_safe/print_message）：作为函数指针目标被间接调用
 * 2. 依赖桩函数（dep_*）：被 stub_dependency.c 中的被测函数直接调用
 */

#include "dep_helpers.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/*============================================================================
 * Basic functions (used as function pointer targets)
 *===========================================================================*/

int add(int a, int b)
{
    return a + b;
}

int sub(int a, int b)
{
    return a - b;
}

int mul(int a, int b)
{
    return a * b;
}

/**
 * @brief 安全除法函数（除数为零时返回0）
 */
int div_safe(int a, int b)
{
    if (b == 0) {
        return 0;
    }
    return a / b;
}

void print_message(const char* msg)
{
    if (msg != NULL) {
        printf("Message: %s\n", msg);
    }
}

/*============================================================================
 * Memory allocation helpers
 *===========================================================================*/

void* malloc_test(size_t size)
{
    if (size == 0) {
        return NULL;
    }
    if (size > 1024 * 1024 * 1024) {
        return NULL;
    }
    return malloc(size);
}

void* null_pointer_return(size_t size)
{
    if (size == 0) {
        return NULL;
    }
    if (size > 1024 * 1024) {
        return NULL;
    }
    return malloc(size);
}

/*============================================================================
 * Stub dependency functions
 *===========================================================================*/

/** 返回单个整型状态码，默认 0。 */
int dep_query_int(void)
{
    return 0;
}

/** 通过出参填充缓冲区，返回状态码，默认成功(0)。 */
int dep_fill_buf(const char* key, char* buf, size_t buf_size)
{
    if (key == NULL || buf == NULL || buf_size == 0) {
        return -1;
    }
    buf[0] = '\0';
    return 0;
}

/** 返回传感器 A 的整型读数，默认 0。 */
int dep_read_sensor_a(void)
{
    return 0;
}

/** 返回传感器 B 的整型读数，默认 0。 */
int dep_read_sensor_b(void)
{
    return 0;
}

/** 获取资源锁，默认成功(0)。 */
int dep_acquire(const char* name)
{
    (void)name;
    return 0;
}

/** 释放资源锁（无操作）。 */
void dep_release(const char* name)
{
    (void)name;
}

/** 读取整数值并写入 *out_val，默认成功(0)并写入 0。 */
int dep_load_value(const char* key, int* out_val)
{
    (void)key;
    if (out_val == NULL) {
        return -1;
    }
    *out_val = 0;
    return 0;
}
