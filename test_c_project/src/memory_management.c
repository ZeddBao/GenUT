/**
 * @file memory_management.c
 * @brief 内存管理测试 - 实现各种内存管理场景，用于单元测试生成
 *
 * 本文件实现内存管理测试的示例函数，涵盖：
 * 1. 分配/释放测试：malloc/calloc/realloc/free、内存泄漏检测
 * 2. 缓冲区操作：内存拷贝、内存比较、内存设置、字符串操作
 * 3. 指针安全测试：NULL解引用、野指针访问、缓冲区溢出、未初始化访问
 */

#include "memory_management.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* ==================== 4.1 分配/释放测试 ==================== */

void* malloc_test(size_t size)
{
    // 模拟分配失败场景
    if (size == 0) {
        return NULL; // 零大小分配
    }

    if (size > 1024 * 1024 * 1024) { // 1GB
        return NULL; // 分配过大，模拟失败
    }

    void* ptr = malloc(size);
    return ptr;
}

void* calloc_test(size_t num, size_t size)
{
    // 模拟分配失败场景
    if (num == 0 || size == 0) {
        return NULL; // 零元素或零大小
    }

    // 检查乘法溢出
    if (size != 0 && num > SIZE_MAX / size) {
        return NULL; // 乘法溢出
    }

    void* ptr = calloc(num, size);
    return ptr;
}

void* realloc_test(void* ptr, size_t new_size)
{
    // 特殊场景：ptr为NULL时相当于malloc
    if (ptr == NULL) {
        return malloc(new_size);
    }

    // 特殊场景：new_size为0时相当于free（但返回NULL）
    if (new_size == 0) {
        free(ptr);
        return NULL;
    }

    void* new_ptr = realloc(ptr, new_size);
    return new_ptr;
}

bool free_test(void* ptr)
{
    // free测试：处理NULL指针
    if (ptr == NULL) {
        // free(NULL)是安全的
        return true;
    }

    // 正常释放
    free(ptr);

    // 注意：这里无法检测是否已释放，仅返回true
    return true;
}

void* memory_leak_test(size_t leak_size)
{
    // 故意分配内存但不释放（模拟内存泄漏）
    if (leak_size == 0) {
        return NULL;
    }

    void* leaked_memory = malloc(leak_size);
    if (leaked_memory != NULL) {
        // 故意不释放，模拟内存泄漏
        // 在实际测试中应检测此泄漏
    }

    return leaked_memory;
}

/* ==================== 4.2 缓冲区操作 ==================== */

/* ----- 内存拷贝 ----- */

void* memcpy_test(void* dest, const void* src, size_t n)
{
    if (dest == NULL || src == NULL) {
        return dest; // 无效参数
    }

    if (n == 0) {
        return dest; // 零长度拷贝
    }

    return memcpy(dest, src, n);
}

void* memmove_test(void* dest, const void* src, size_t n)
{
    if (dest == NULL || src == NULL) {
        return dest; // 无效参数
    }

    if (n == 0) {
        return dest; // 零长度移动
    }

    // memmove处理内存重叠
    return memmove(dest, src, n);
}

/* ----- 内存比较 ----- */

int memcmp_test(const void* ptr1, const void* ptr2, size_t n)
{
    if (ptr1 == NULL || ptr2 == NULL) {
        // 定义NULL指针比较的行为
        if (ptr1 == ptr2) {
            return 0; // 两个都是NULL
        } else if (ptr1 == NULL) {
            return -1; // ptr1为NULL，ptr2非NULL
        } else {
            return 1; // ptr1非NULL，ptr2为NULL
        }
    }

    if (n == 0) {
        return 0; // 零长度比较
    }

    return memcmp(ptr1, ptr2, n);
}

/* ----- 内存设置 ----- */

void* memset_test(void* ptr, int value, size_t num)
{
    if (ptr == NULL) {
        return NULL; // 无效参数
    }

    if (num == 0) {
        return ptr; // 零长度设置
    }

    return memset(ptr, value, num);
}

/* ----- 字符串操作 ----- */

char* strcpy_test(char* dest, const char* src)
{
    if (dest == NULL || src == NULL) {
        return dest; // 无效参数
    }

    // 注意：strcpy不检查目标缓冲区大小，可能溢出
    return strcpy(dest, src);
}

char* strcat_test(char* dest, const char* src)
{
    if (dest == NULL || src == NULL) {
        return dest; // 无效参数
    }

    // 注意：strcat不检查目标缓冲区大小，可能溢出
    return strcat(dest, src);
}

size_t strlen_test(const char* str)
{
    if (str == NULL) {
        return 0; // NULL指针
    }

    return strlen(str);
}

/* ==================== 4.3 指针安全测试 ==================== */

int null_dereference_test(const int* ptr)
{
    // 防御性编程：检查NULL指针
    if (ptr == NULL) {
        return -1;
    }

    // 安全解引用
    return *ptr;
}

int wild_pointer_test(size_t size)
{
    // 注意：此函数可能产生未定义行为，仅用于测试
    if (size == 0) {
        return -1;
    }

    int* ptr = (int*)malloc(size * sizeof(int));
    if (ptr == NULL) {
        return -2;
    }

    // 初始化内存
    for (size_t i = 0; i < size; i++) {
        ptr[i] = (int)i;
    }

    int value = ptr[0]; // 读取有效值
    free(ptr); // 释放内存

    // 危险：访问已释放的内存（野指针）
    // 注意：这是未定义行为，实际代码中绝不应该这样做
    // 这里仅为了演示测试场景
    int dangerous_value = 0;
    // 为了安全，注释掉实际访问
    // dangerous_value = ptr[0]; // 可能崩溃或返回垃圾值

    return value; // 返回释放前读取的值
}

bool buffer_overflow_test(size_t buffer_size, size_t write_size)
{
    if (buffer_size == 0 || write_size == 0) {
        return false;
    }

    char* buffer = (char*)malloc(buffer_size);
    if (buffer == NULL) {
        return false;
    }

    // 安全初始化缓冲区
    memset(buffer, 0, buffer_size);

    bool overflow_detected = false;

    // 检查写入大小是否超过缓冲区大小
    if (write_size > buffer_size) {
        overflow_detected = true;
        // 注意：实际不应执行溢出写入
        // 这里仅标记检测到溢出
    } else {
        // 安全写入
        memset(buffer, 'A', write_size);
    }

    free(buffer);
    return overflow_detected;
}

int uninitialized_access_test(bool init_value)
{
    int* ptr = (int*)malloc(sizeof(int));
    if (ptr == NULL) {
        return -1;
    }

    // 根据参数决定是否初始化
    if (init_value) {
        *ptr = 42;
    }
    // 否则保持未初始化

    int value = 0;
    if (init_value) {
        value = *ptr; // 读取已初始化的值
    } else {
        // 危险：读取未初始化的内存
        // 注意：这是未定义行为，可能返回任意值
        // 为了安全，我们返回一个标记值
        value = 0xDEADBEEF; // 标记值，表示未初始化访问
    }

    free(ptr);
    return value;
}

int pointer_arithmetic_test(const int* array, int size, int offset)
{
    if (array == NULL || size <= 0) {
        return -1;
    }

    // 检查偏移量是否在有效范围内
    if (offset < 0 || offset >= size) {
        return -2; // 偏移越界
    }

    // 安全的指针算术运算
    const int* ptr = array + offset;
    return *ptr;
}

bool double_free_test(size_t size)
{
    if (size == 0) {
        return false;
    }

    void* ptr = malloc(size);
    if (ptr == NULL) {
        return false;
    }

    // 第一次释放
    free(ptr);

    // 危险：双重释放
    // 注意：这是未定义行为，可能崩溃
    // 为了安全，注释掉第二次释放
    // free(ptr); // 可能崩溃

    // 返回true表示"执行"了双重释放（实际上没有）
    return true;
}