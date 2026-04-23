/**
 * @file error_handling.c
 * @brief 错误处理测试 - 实现各种错误处理场景，用于单元测试生成
 *
 * 本文件实现错误处理测试的示例函数，涵盖：
 * 1. 输入验证：NULL指针检查、范围检查、长度检查、格式检查
 * 2. 错误路径：资源分配失败、文件操作失败、系统调用失败
 * 3. 异常情况：除零错误、溢出测试、下溢测试、无效转换
 */

#include "error_handling.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>
#include <stdio.h>

/* ==================== 5.1 输入验证 ==================== */

int null_pointer_check(const int* data, int length)
{
    // NULL指针检查
    if (data == NULL) {
        return -1;
    }

    // 长度检查
    if (length <= 0) {
        return -2;
    }

    // 计算数据总和
    int sum = 0;
    for (int i = 0; i < length; i++) {
        sum += data[i];
    }

    return sum;
}

int range_check(int value, int min, int max)
{
    // 范围检查
    if (value < min) {
        return min; // 低于最小值，返回最小值
    } else if (value > max) {
        return max; // 高于最大值，返回最大值
    } else {
        return value; // 在范围内，返回原值
    }
}

bool length_check(const void* buffer, size_t buffer_size, size_t required_size)
{
    // 缓冲区指针检查
    if (buffer == NULL && required_size > 0) {
        return false;
    }

    // 长度检查
    return buffer_size >= required_size;
}

bool format_check(const char* str)
{
    // NULL指针检查
    if (str == NULL) {
        return false;
    }

    // 空字符串检查
    if (str[0] == '\0') {
        return false;
    }

    // 简单格式检查：字符串必须至少包含一个字母和一个数字
    bool has_letter = false;
    bool has_digit = false;

    for (int i = 0; str[i] != '\0'; i++) {
        if (isalpha((unsigned char)str[i])) {
            has_letter = true;
        } else if (isdigit((unsigned char)str[i])) {
            has_digit = true;
        }

        // 如果已经满足条件，提前退出
        if (has_letter && has_digit) {
            break;
        }
    }

    return has_letter && has_digit;
}

/* ==================== 5.2 错误路径测试 ==================== */

void* file_operation_failure_test(const char* filename, const char* mode)
{
    // 模拟文件操作失败
    if (filename == NULL || mode == NULL) {
        return NULL; // 无效参数
    }

    // 模拟特定文件名导致失败
    if (strcmp(filename, "/dev/null") == 0) {
        // 特殊文件名，模拟成功
        // 注意：实际不会打开文件，仅返回非NULL指针
        static FILE dummy_file;
        return &dummy_file;
    } else if (strcmp(filename, "/invalid/path") == 0) {
        // 无效路径，模拟失败
        return NULL;
    }

    // 默认模拟失败
    return NULL;
}

int system_call_failure_test(int operation)
{
    // 模拟系统调用失败，设置不同的errno值
    switch (operation) {
        case 0:
            // 成功
            errno = 0;
            return 0;

        case 1:
            // 权限不足
            errno = EACCES;
            return -1;

        case 2:
            // 文件不存在
            errno = ENOENT;
            return -1;

        case 3:
            // 资源暂时不可用
            errno = EAGAIN;
            return -1;

        case 4:
            // 内存不足
            errno = ENOMEM;
            return -1;

        case 5:
            // 参数无效
            errno = EINVAL;
            return -1;

        default:
            // 未知错误
            errno = EIO;
            return -1;
    }
}

/* ==================== 5.3 异常情况测试 ==================== */

int integer_overflow_test(int a, int b)
{
    // 整数溢出测试（加法）
    // 注意：有符号整数溢出是未定义行为，这里使用条件检查

    if (a > 0 && b > 0) {
        // 检查正数加法溢出
        if (a > INT_MAX - b) {
            return INT_MAX; // 溢出，返回最大值
        }
    } else if (a < 0 && b < 0) {
        // 检查负数加法溢出（下溢）
        if (a < INT_MIN - b) {
            return INT_MIN; // 下溢，返回最小值
        }
    }

    return a + b;
}

int integer_underflow_test(int a, int b)
{
    // 整数下溢测试（减法）
    // 注意：有符号整数下溢是未定义行为，这里使用条件检查

    if (a >= 0 && b < 0) {
        // a - (-b) = a + b，检查加法溢出
        if (a > INT_MAX + b) { // 注意：b是负数
            return INT_MAX;
        }
    } else if (a < 0 && b > 0) {
        // (-a) - b = -(a + b)，检查加法溢出
        if (a < INT_MIN + b) { // 注意：a是负数
            return INT_MIN;
        }
    }

    return a - b;
}

float float_overflow_test(float a, float multiplier)
{
    // 浮点溢出测试
    // 注意：浮点数溢出会得到inf，这里使用条件检查

    if (multiplier == 0.0f) {
        return 0.0f;
    }

    // 检查是否会溢出到inf
    float result = a * multiplier;

    // 简化检查：如果结果非常大，返回最大值
    if (result > 1e38f) { // FLT_MAX约为3.4e38
        return 1e38f;
    } else if (result < -1e38f) {
        return -1e38f;
    }

    return result;
}

float float_underflow_test(float a, float divisor)
{
    // 浮点下溢测试
    if (divisor == 0.0f) {
        return 0.0f; // 避免除零
    }

    float result = a / divisor;

    // 检查是否下溢到0
    if (result > 0 && result < 1e-38f) { // FLT_MIN约为1.2e-38
        return 1e-38f;
    } else if (result < 0 && result > -1e-38f) {
        return -1e-38f;
    }

    return result;
}

int invalid_conversion_test(const char* str)
{
    // 无效转换测试：字符串转整数
    if (str == NULL) {
        return 0;
    }

    // 简单转换：只处理纯数字字符串
    for (int i = 0; str[i] != '\0'; i++) {
        if (!isdigit((unsigned char)str[i])) {
            return 0; // 包含非数字字符，转换失败
        }
    }

    // 简单转换（实际应使用strtol等函数）
    int result = 0;
    for (int i = 0; str[i] != '\0'; i++) {
        result = result * 10 + (str[i] - '0');
    }

    return result;
}