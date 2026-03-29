/**
 * @file error_handling.h
 * @brief 错误处理测试 - 演示各种错误处理场景，用于单元测试生成
 *
 * 本头文件包含错误处理测试的示例函数声明，涵盖：
 * 1. 输入验证：NULL指针检查、范围检查、长度检查、格式检查
 * 2. 错误路径：资源分配失败、文件操作失败、系统调用失败
 * 3. 异常情况：除零错误、溢出测试、下溢测试、无效转换
 */

#ifndef ERROR_HANDLING_H
#define ERROR_HANDLING_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ==================== 5.1 输入验证 ==================== */

/**
 * @brief NULL指针检查测试
 * @param data 数据指针（可能为NULL）
 * @param length 数据长度
 * @return 有效数据的总和，如果指针为NULL则返回-1
 */
int null_pointer_check(const int* data, int length);

/**
 * @brief 范围检查测试：参数值域验证
 * @param value 要检查的值
 * @param min 最小值（包含）
 * @param max 最大值（包含）
 * @return 如果在范围内返回value，否则返回边界值
 */
int range_check(int value, int min, int max);

/**
 * @brief 长度检查测试：数组/缓冲区长度验证
 * @param buffer 缓冲区指针
 * @param buffer_size 缓冲区大小
 * @param required_size 所需大小
 * @return 如果缓冲区足够大返回true，否则返回false
 */
bool length_check(const void* buffer, size_t buffer_size, size_t required_size);

/**
 * @brief 格式检查测试：字符串格式验证
 * @param str 要检查的字符串
 * @return 如果字符串格式正确返回true，否则返回false
 */
bool format_check(const char* str);

/* ==================== 5.2 错误路径测试 ==================== */

/**
 * @brief 资源分配失败测试：malloc返回NULL
 * @param size 要分配的大小
 * @return 成功返回分配的内存指针，失败返回NULL
 */
void* allocation_failure_test(size_t size);

/**
 * @brief 文件操作失败测试：模拟fopen失败
 * @param filename 文件名
 * @param mode 打开模式
 * @return 成功返回文件指针，失败返回NULL
 */
void* file_operation_failure_test(const char* filename, const char* mode);

/**
 * @brief 系统调用失败测试：模拟errno各种值
 * @param operation 操作类型
 * @return 成功返回0，失败返回错误码
 */
int system_call_failure_test(int operation);

/* ==================== 5.3 异常情况测试 ==================== */

/**
 * @brief 除零错误测试：分母为零的情况
 * @param numerator 分子
 * @param denominator 分母
 * @return 除法结果，如果分母为零则返回0
 */
int divide_by_zero_test(int numerator, int denominator);

/**
 * @brief 整数溢出测试：加法溢出
 * @param a 第一个加数
 * @param b 第二个加数
 * @return 加法结果，如果溢出则返回边界值
 */
int integer_overflow_test(int a, int b);

/**
 * @brief 整数下溢测试：减法下溢
 * @param a 被减数
 * @param b 减数
 * @return 减法结果，如果下溢则返回边界值
 */
int integer_underflow_test(int a, int b);

/**
 * @brief 浮点溢出测试：浮点数过大
 * @param a 浮点数值
 * @param multiplier 乘数
 * @return 乘法结果，如果溢出则返回边界值
 */
float float_overflow_test(float a, float multiplier);

/**
 * @brief 浮点下溢测试：浮点数过小
 * @param a 浮点数值
 * @param divisor 除数
 * @return 除法结果，如果下溢则返回边界值
 */
float float_underflow_test(float a, float divisor);

/**
 * @brief 无效转换测试：类型转换错误
 * @param str 字符串
 * @return 转换后的整数值，如果转换失败则返回0
 */
int invalid_conversion_test(const char* str);

#ifdef __cplusplus
}
#endif

#endif /* ERROR_HANDLING_H */