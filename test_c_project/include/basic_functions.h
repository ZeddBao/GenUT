/**
 * @file basic_functions.h
 * @brief 基础函数测试 - 演示各种基础函数场景，用于单元测试生成
 *
 * 本头文件包含基础函数测试的示例函数声明，涵盖：
 * 1. 纯函数、无参数函数、void函数
 * 2. 各种参数类型：基本类型、指针、数组、结构体、枚举、联合体、位字段
 * 3. 各种返回值：正常返回值、错误码、NULL指针、布尔值
 */

#ifndef BASIC_FUNCTIONS_H
#define BASIC_FUNCTIONS_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ==================== 1.1 简单函数测试 ==================== */

/**
 * @brief 无参数函数示例：测试全局状态变化或常量返回值
 * @return 固定的常量值
 */
int no_parameter_function(void);

/**
 * @brief void函数示例：测试副作用和状态改变
 * @param count 计数器指针，函数会修改其值
 */
void void_function_with_side_effect(int* count);

/* ==================== 1.2 参数类型测试 ==================== */

/* ----- 基本类型 ----- */

/**
 * @brief 测试多种基本类型参数
 * @param i 整数
 * @param f 浮点数
 * @param d 双精度浮点数
 * @param c 字符
 * @param b 布尔值
 * @return 计算结果
 */
int basic_types_function(int i, float f, double d, char c, bool b);

/* ----- 指针类型 ----- */

/**
 * @brief 测试指针参数
 * @param ptr 整数指针
 * @return 指针指向的值，如果指针为NULL则返回-1
 */
int pointer_parameter_function(const int* ptr);

/**
 * @brief 测试返回指针的函数
 * @param value 要存储的值
 * @return 指向静态存储的指针（注意：非线程安全）
 */
int* pointer_return_function(int value);

/* ----- 数组参数 ----- */

/**
 * @brief 测试定长数组参数
 * @param arr 长度为10的整数数组
 * @return 数组第一个元素的值
 */
int fixed_array_function(int arr[10]);

/**
 * @brief 测试指针+长度参数（动态数组）
 * @param arr 数组指针
 * @param len 数组长度
 * @return 数组元素之和
 */
int dynamic_array_function(const int* arr, int len);

/* ----- 结构体参数 ----- */

/** 简单结构体定义 */
typedef struct {
    int x;
    int y;
} Point;

/**
 * @brief 测试结构体值传递
 * @param p 点结构体
 * @return 点到原点的曼哈顿距离
 */
int struct_by_value_function(Point p);

/**
 * @brief 测试结构体指针传递
 * @param p 点结构体指针
 * @return 点到原点的曼哈顿距离，如果指针为NULL则返回-1
 */
int struct_by_pointer_function(const Point* p);

/* ----- 枚举类型 ----- */

/** 颜色枚举定义 */
typedef enum {
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_YELLOW,
    COLOR_COUNT
} Color;

/**
 * @brief 测试枚举参数
 * @param color 颜色枚举值
 * @return 颜色对应的数值代码
 */
int enum_function(Color color);

/* ----- 联合体参数 ----- */

/** 联合体定义：可以存储整数或浮点数 */
typedef union {
    int int_value;
    float float_value;
} NumberUnion;

/**
 * @brief 测试联合体参数
 * @param num 数字联合体
 * @param is_float 是否作为浮点数解释
 * @return 整数值
 */
int union_function(NumberUnion num, bool is_float);

/* ----- 位字段参数 ----- */

/** 位字段结构体定义 */
typedef struct {
    unsigned int flag1 : 1;  // 1位标志
    unsigned int flag2 : 2;  // 2位标志
    unsigned int flag3 : 3;  // 3位标志
} BitField;

/**
 * @brief 测试位字段参数
 * @param bf 位字段结构体
 * @return 组合后的标志值
 */
int bitfield_function(BitField bf);

/* ==================== 1.3 返回值测试 ==================== */

/**
 * @brief 正常返回值示例：各种边界值和典型值
 * @param value 输入值
 * @return 处理后的值，根据输入不同返回不同值
 */
int normal_return_function(int value);

/**
 * @brief 错误码返回示例：负数、特定错误码
 * @param operation 操作类型
 * @return 成功返回0，失败返回负数错误码
 */
int error_code_return_function(int operation);

/**
 * @brief 布尔返回值示例：true/false分支
 * @param condition 条件值
 * @return 条件是否为真
 */
bool boolean_return_function(int condition);

#ifdef __cplusplus
}
#endif

#endif /* BASIC_FUNCTIONS_H */