/**
 * 嵌套结构体测试头文件
 */

#ifndef NESTED_STRUCT_TEST_H
#define NESTED_STRUCT_TEST_H

#include <stdint.h>

// 简单嵌套结构体
typedef struct {
    int value;
} InnerStruct;

typedef struct {
    InnerStruct inner;
} NestedContainer;

// 多层嵌套结构体
typedef struct {
    int value;
} Level3;

typedef struct {
    Level3 level3;
} Level2;

typedef struct {
    Level2 level2;
} Level1;

typedef struct {
    Level1 level1;
} MultiLevel;

// 指针嵌套结构体
typedef struct {
    int data;
} DataStruct;

typedef struct {
    DataStruct* inner_ptr;
} PointerContainer;

// 混合访问结构体
typedef struct {
    int value;
} MixedInner;

typedef struct {
    MixedInner inner;
} MixedMiddle;

typedef struct {
    int count;
} DataInfo;

typedef struct {
    MixedMiddle middle;
    DataInfo data;
} OuterStruct;

// 数组嵌套结构体
typedef struct {
    InnerStruct inner;
} ItemStruct;

typedef struct {
    ItemStruct items[5];
} ArrayContainer;

// 函数声明
int test_nested_struct_simple(NestedContainer* container);
int test_multi_level_nested(MultiLevel* ml);
int test_nested_struct_pointer(PointerContainer* pc);
int test_mixed_access(OuterStruct outer);
int test_array_nested(ArrayContainer* ac, int index);

#endif // NESTED_STRUCT_TEST_H