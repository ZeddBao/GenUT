/**
 * 嵌套结构体测试文件
 * 用于验证嵌套结构体字段访问和约束提取
 */

#include "nested_struct_test.h"
#include <stdio.h>

// 简单嵌套结构体测试
int test_nested_struct_simple(NestedContainer* container) {
    if (container == NULL) {
        return -1;
    }

    // 访问嵌套字段：container->inner.value
    if (container->inner.value > 100) {
        return 1;
    } else if (container->inner.value < 0) {
        return -1;
    } else {
        return 0;
    }
}

// 多层嵌套结构体测试
int test_multi_level_nested(MultiLevel* ml) {
    if (ml == NULL) {
        return -1;
    }

    // 访问多层嵌套字段：ml->level1.level2.level3.value
    if (ml->level1.level2.level3.value > 500) {
        return 100;
    } else if (ml->level1.level2.level3.value < 100) {
        return -100;
    } else {
        return ml->level1.level2.level3.value;
    }
}

// 结构体指针嵌套测试
int test_nested_struct_pointer(PointerContainer* pc) {
    if (pc == NULL || pc->inner_ptr == NULL) {
        return -1;
    }

    // 访问指针嵌套字段：pc->inner_ptr->data
    if (pc->inner_ptr->data > 200) {
        return 1;
    } else if (pc->inner_ptr->data < 50) {
        return -1;
    } else {
        return 0;
    }
}

// 混合访问测试（点操作符和箭头操作符）
int test_mixed_access(OuterStruct outer) {
    // 访问嵌套字段：outer.middle.inner.value
    if (outer.middle.inner.value > 300) {
        return 10;
    } else if (outer.middle.inner.value < 100) {
        return -10;
    }

    // 访问另一组嵌套字段：outer.data.count
    if (outer.data.count > 10) {
        return 20;
    }

    return 0;
}

// 数组嵌套结构体测试
int test_array_nested(ArrayContainer* ac, int index) {
    if (ac == NULL || index < 0 || index >= 5) {
        return -1;
    }

    // 访问数组元素中的嵌套字段：ac->items[index].inner.value
    if (ac->items[index].inner.value > 400) {
        return 1;
    }

    return 0;
}