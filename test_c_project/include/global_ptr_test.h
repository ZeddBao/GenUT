#ifndef GLOBAL_PTR_TEST_H
#define GLOBAL_PTR_TEST_H

#include <stdint.h>
#include <stddef.h>

/* 全局指针测试结构体 */
typedef struct {
    int32_t value;
    int32_t threshold;
    uint8_t enabled;
    char status;
} GlobalData;

typedef struct {
    GlobalData* data;
    int32_t count;
    int32_t capacity;
} DataContainer;

typedef struct {
    int32_t x;
    int32_t y;
    int32_t z;
} Point3D;

/* 全局指针变量声明 */
extern GlobalData* g_global_data_ptr;
extern DataContainer* g_data_container_ptr;
extern Point3D** g_point_ptr_ptr;  /* 二级指针 */
extern int32_t* g_int_array_ptr;
extern const char* g_string_ptr;

/* 测试函数声明 */

/**
 * 测试全局指针是否为NULL的条件分支
 * 如果指针为NULL返回-1，否则返回指针指向的值
 */
int32_t test_ptr_null_check(void);

/**
 * 测试全局指针指向的结构体字段条件
 * 根据value和threshold的比较结果返回不同值
 */
int32_t test_ptr_field_condition(void);

/**
 * 测试二级指针（指针的指针）的条件
 * 通过**ptr访问最终数据
 */
int32_t test_double_ptr_condition(void);

/**
 * 测试全局数组指针的条件
 * 检查数组第一个元素和大小
 */
int32_t test_array_ptr_condition(void);

/**
 * 测试字符串指针（const char*）的条件
 * 检查字符串是否为空或特定内容
 */
int32_t test_string_ptr_condition(void);

/**
 * 测试复杂条件：多个全局指针的组合条件
 * 使用逻辑运算符连接多个指针条件
 */
int32_t test_multi_ptr_condition(void);

/**
 * 测试指针字段的嵌套访问
 * g_data_container_ptr->data->value等
 */
int32_t test_nested_ptr_field(void);

/**
 * 测试指针运算和条件
 * 使用指针偏移访问数组元素
 */
int32_t test_ptr_arithmetic_condition(void);

/**
 * 测试指针类型转换和条件
 * 将void*转换为具体类型指针后判断
 */
int32_t test_ptr_cast_condition(void);

#endif // GLOBAL_PTR_TEST_H