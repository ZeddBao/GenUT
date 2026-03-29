/**
 * @file memory_management.h
 * @brief 内存管理测试 - 演示各种内存管理场景，用于单元测试生成
 *
 * 本头文件包含内存管理测试的示例函数声明，涵盖：
 * 1. 分配/释放测试：malloc/calloc/realloc/free、内存泄漏检测
 * 2. 缓冲区操作：内存拷贝、内存比较、内存设置、字符串操作
 * 3. 指针安全测试：NULL解引用、野指针访问、缓冲区溢出、未初始化访问
 */

#ifndef MEMORY_MANAGEMENT_H
#define MEMORY_MANAGEMENT_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ==================== 4.1 分配/释放测试 ==================== */

/**
 * @brief malloc分配测试：分配成功/失败场景
 * @param size 要分配的内存大小
 * @return 成功返回分配的内存指针，失败返回NULL
 */
void* malloc_test(size_t size);

/**
 * @brief calloc分配测试：分配并清零内存
 * @param num 元素数量
 * @param size 每个元素的大小
 * @return 成功返回分配的内存指针，失败返回NULL
 */
void* calloc_test(size_t num, size_t size);

/**
 * @brief realloc测试：扩展/缩小内存块
 * @param ptr 原内存指针（可为NULL）
 * @param new_size 新的大小
 * @return 成功返回重新分配的内存指针，失败返回NULL
 */
void* realloc_test(void* ptr, size_t new_size);

/**
 * @brief free测试：NULL指针、重复释放场景
 * @param ptr 要释放的内存指针
 * @return 是否成功释放（仅用于测试，实际free无返回值）
 */
bool free_test(void* ptr);

/**
 * @brief 内存泄漏检测：分配未释放场景
 * @param leak_size 要泄漏的内存大小
 * @return 分配的内存指针（故意不释放）
 */
void* memory_leak_test(size_t leak_size);

/* ==================== 4.2 缓冲区操作 ==================== */

/* ----- 内存拷贝 ----- */

/**
 * @brief memcpy测试：拷贝边界测试
 * @param dest 目标缓冲区
 * @param src 源缓冲区
 * @param n 要拷贝的字节数
 * @return 目标缓冲区指针
 */
void* memcpy_test(void* dest, const void* src, size_t n);

/**
 * @brief memmove测试：处理内存重叠区域
 * @param dest 目标缓冲区
 * @param src 源缓冲区
 * @param n 要移动的字节数
 * @return 目标缓冲区指针
 */
void* memmove_test(void* dest, const void* src, size_t n);

/* ----- 内存比较 ----- */

/**
 * @brief memcmp测试：内存比较返回值
 * @param ptr1 第一个内存块
 * @param ptr2 第二个内存块
 * @param n 要比较的字节数
 * @return 比较结果：<0, 0, >0
 */
int memcmp_test(const void* ptr1, const void* ptr2, size_t n);

/* ----- 内存设置 ----- */

/**
 * @brief memset测试：各种模式设置
 * @param ptr 内存指针
 * @param value 要设置的值
 * @param num 要设置的字节数
 * @return 原指针
 */
void* memset_test(void* ptr, int value, size_t num);

/* ----- 字符串操作 ----- */

/**
 * @brief strcpy测试：字符串拷贝边界
 * @param dest 目标缓冲区
 * @param src 源字符串
 * @return 目标缓冲区指针
 */
char* strcpy_test(char* dest, const char* src);

/**
 * @brief strcat测试：字符串连接边界
 * @param dest 目标缓冲区
 * @param src 源字符串
 * @return 目标缓冲区指针
 */
char* strcat_test(char* dest, const char* src);

/**
 * @brief strlen测试：字符串长度计算
 * @param str 字符串
 * @return 字符串长度
 */
size_t strlen_test(const char* str);

/* ==================== 4.3 指针安全测试 ==================== */

/**
 * @brief NULL解引用测试：防御性编程测试
 * @param ptr 可能为NULL的指针
 * @return 指针指向的值，如果指针为NULL则返回-1
 */
int null_dereference_test(const int* ptr);

/**
 * @brief 野指针访问测试：已释放内存访问
 * @param size 要分配的大小
 * @return 访问已释放内存的结果（可能崩溃）
 */
int wild_pointer_test(size_t size);

/**
 * @brief 缓冲区溢出测试：读写越界
 * @param buffer_size 缓冲区大小
 * @param write_size 写入大小
 * @return 是否检测到溢出
 */
bool buffer_overflow_test(size_t buffer_size, size_t write_size);

/**
 * @brief 未初始化访问测试：读取未初始化内存
 * @param init_value 是否初始化内存
 * @return 读取到的值（可能未定义）
 */
int uninitialized_access_test(bool init_value);

/**
 * @brief 指针算术测试：指针加减运算
 * @param array 数组
 * @param size 数组大小
 * @param offset 偏移量
 * @return 偏移后的指针指向的值
 */
int pointer_arithmetic_test(const int* array, int size, int offset);

/**
 * @brief 双重释放测试：重复释放同一内存
 * @param size 要分配的大小
 * @return 是否成功执行双重释放（可能崩溃）
 */
bool double_free_test(size_t size);

#ifdef __cplusplus
}
#endif

#endif /* MEMORY_MANAGEMENT_H */