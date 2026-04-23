/**
 * @file basic_functions.c
 * @brief 基础函数测试 - 实现各种基础函数场景，用于单元测试生成
 *
 * 本文件实现基础函数测试的示例函数，涵盖：
 * 1. 纯函数、无参数函数、void函数
 * 2. 各种参数类型：基本类型、指针、数组、结构体、枚举、联合体、位字段
 * 3. 各种返回值：正常返回值、错误码、NULL指针、布尔值
 */

#include "basic_functions.h"
#include <stdlib.h>
#include <string.h>

/* ==================== 全局状态（用于测试副作用） ==================== */
static int global_counter = 0;

/* ==================== 1.1 简单函数测试 ==================== */

/**
 * @brief 无参数函数示例：测试全局状态变化或常量返回值
 */
int no_parameter_function(void)
{
    // 无参数函数：可能依赖全局状态或返回常量
    return 42; // 返回固定值
}

/**
 * @brief void函数示例：测试副作用和状态改变
 */
void void_function_with_side_effect(int* count)
{
    // void函数：通过指针参数产生副作用
    if (count != NULL) {
        *count += 1;
        global_counter += 1;
    }
}

/* ==================== 1.2 参数类型测试 ==================== */

/* ----- 基本类型 ----- */

/**
 * @brief 测试多种基本类型参数
 */
int basic_types_function(int i, float f, double d, char c, bool b)
{
    int result = 0;

    // 处理整数参数
    if (i > 0) {
        result += i;
    } else {
        result -= i;
    }

    // 处理浮点数参数
    if (f > 0.0f) {
        result += (int)f;
    }

    // 处理双精度参数
    if (d < 100.0) {
        result += (int)d;
    }

    // 处理字符参数
    if (c == 'A' || c == 'a') {
        result += 10;
    }

    // 处理布尔参数
    if (b) {
        result *= 2;
    }

    return result;
}

/* ----- 指针类型 ----- */

/**
 * @brief 测试指针参数
 */
int pointer_parameter_function(const int* ptr)
{
    // 检查NULL指针
    if (ptr == NULL) {
        return -1;
    }

    // 返回指针指向的值
    return *ptr;
}

/**
 * @brief 测试返回指针的函数
 */
int* pointer_return_function(int value)
{
    static int storage[10];
    static int index = 0;

    // 模拟存储值并返回指针
    if (index < 10) {
        storage[index] = value;
        return &storage[index++];
    }

    // 缓冲区已满，返回NULL
    return NULL;
}

/* ----- 数组参数 ----- */

/**
 * @brief 测试定长数组参数
 */
int fixed_array_function(int arr[10])
{
    // 检查数组第一个元素
    if (arr[0] > 0) {
        return arr[0];
    } else {
        return -arr[0];
    }
}

/**
 * @brief 测试指针+长度参数（动态数组）
 */
int dynamic_array_function(const int* arr, int len)
{
    // 检查参数有效性
    if (arr == NULL || len <= 0) {
        return 0;
    }

    // 计算数组元素之和
    int sum = 0;
    for (int i = 0; i < len; i++) {
        sum += arr[i];
    }

    return sum;
}

/* ----- 结构体参数 ----- */

/**
 * @brief 测试结构体值传递
 */
int struct_by_value_function(Point p)
{
    // 计算曼哈顿距离
    int distance = 0;

    if (p.x >= 0) {
        distance += p.x;
    } else {
        distance -= p.x;
    }

    if (p.y >= 0) {
        distance += p.y;
    } else {
        distance -= p.y;
    }

    return distance;
}

/**
 * @brief 测试结构体指针传递
 */
int struct_by_pointer_function(const Point* p)
{
    // 检查NULL指针
    if (p == NULL) {
        return -1;
    }

    // 计算曼哈顿距离
    int distance = 0;

    if (p->x >= 0) {
        distance += p->x;
    } else {
        distance -= p->x;
    }

    if (p->y >= 0) {
        distance += p->y;
    } else {
        distance -= p->y;
    }

    return distance;
}

/* ----- 枚举类型 ----- */

/**
 * @brief 测试枚举参数
 */
int enum_function(Color color)
{
    // 根据颜色返回不同的代码
    switch (color) {
        case COLOR_RED:
            return 1;
        case COLOR_GREEN:
            return 2;
        case COLOR_BLUE:
            return 3;
        case COLOR_YELLOW:
            return 4;
        default:
            return 0; // 未知颜色
    }
}

/* ----- 联合体参数 ----- */

/**
 * @brief 测试联合体参数
 */
int union_function(NumberUnion num, bool is_float)
{
    if (is_float) {
        // 作为浮点数解释
        if (num.float_value > 0.0f) {
            return (int)num.float_value;
        } else {
            return -(int)num.float_value;
        }
    } else {
        // 作为整数解释
        if (num.int_value > 0) {
            return num.int_value;
        } else {
            return -num.int_value;
        }
    }
}

/* ----- 位字段参数 ----- */

/**
 * @brief 测试位字段参数
 */
int bitfield_function(BitField bf)
{
    int result = 0;

    // 组合各个位字段
    result |= (bf.flag1 & 0x1);
    result |= (bf.flag2 & 0x3) << 1;
    result |= (bf.flag3 & 0x7) << 3;

    return result;
}

/* ==================== 1.3 返回值测试 ==================== */

/**
 * @brief 正常返回值示例：各种边界值和典型值
 */
int normal_return_function(int value)
{
    // 根据输入值返回不同的结果
    if (value > 100) {
        return value * 2;
    } else if (value > 0) {
        return value;
    } else if (value == 0) {
        return 0;
    } else {
        return -value;
    }
}

/**
 * @brief 错误码返回示例：负数、特定错误码
 */
int error_code_return_function(int operation)
{
    // 模拟不同操作的结果
    switch (operation) {
        case 0:
            return 0; // 成功
        case 1:
            return -1; // 一般错误
        case 2:
            return -2; // 参数错误
        case 3:
            return -3; // 资源不足
        case 4:
            return -4; // 超时
        default:
            return -99; // 未知错误
    }
}

/**
 * @brief 布尔返回值示例：true/false分支
 */
bool boolean_return_function(int condition)
{
    // 根据条件返回布尔值
    if (condition > 0) {
        return true;
    } else if (condition < 0) {
        return false;
    } else {
        // condition == 0
        return false;
    }
}