#include "global_ptr_test.h"
#include <stdio.h>
#include <string.h>

/* 全局指针变量定义 */
GlobalData* g_global_data_ptr = NULL;
DataContainer* g_data_container_ptr = NULL;
Point3D** g_point_ptr_ptr = NULL;
int32_t* g_int_array_ptr = NULL;
const char* g_string_ptr = NULL;

/* 辅助函数：创建默认数据用于测试 */
static GlobalData* create_default_global_data(void) {
    static GlobalData default_data = {
        .value = 100,
        .threshold = 50,
        .enabled = 1,
        .status = 'A'
    };
    return &default_data;
}

static DataContainer* create_default_container(void) {
    static DataContainer default_container = {
        .data = NULL,
        .count = 0,
        .capacity = 10
    };
    static GlobalData container_data = {
        .value = 200,
        .threshold = 150,
        .enabled = 1,
        .status = 'B'
    };
    default_container.data = &container_data;
    default_container.count = 1;
    return &default_container;
}

static Point3D* create_default_point(void) {
    static Point3D default_point = {
        .x = 10,
        .y = 20,
        .z = 30
    };
    return &default_point;
}

static int32_t* create_default_int_array(void) {
    static int32_t default_array[5] = {1, 2, 3, 4, 5};
    return default_array;
}

/* 测试函数实现 */

int32_t test_ptr_null_check(void) {
    /* 分支1: 指针为NULL */
    if (g_global_data_ptr == NULL) {
        printf("Global data pointer is NULL\n");
        return -1;
    }

    /* 分支2: 指针不为NULL */
    printf("Global data pointer is valid\n");

    /* 嵌套分支: 根据指针指向的字段进一步判断 */
    if (g_global_data_ptr->value > 0) {
        return g_global_data_ptr->value;
    } else {
        return 0;
    }
}

int32_t test_ptr_field_condition(void) {
    /* 必须检查指针是否有效 */
    if (g_global_data_ptr == NULL) {
        return -1;
    }

    /* 分支1: value > threshold */
    if (g_global_data_ptr->value > g_global_data_ptr->threshold) {
        printf("Value %d exceeds threshold %d\n",
               g_global_data_ptr->value, g_global_data_ptr->threshold);
        return 1;
    }
    /* 分支2: value == threshold */
    else if (g_global_data_ptr->value == g_global_data_ptr->threshold) {
        printf("Value %d equals threshold %d\n",
               g_global_data_ptr->value, g_global_data_ptr->threshold);
        return 0;
    }
    /* 分支3: value < threshold */
    else {
        printf("Value %d below threshold %d\n",
               g_global_data_ptr->value, g_global_data_ptr->threshold);
        return -1;
    }
}

int32_t test_double_ptr_condition(void) {
    /* 检查二级指针是否为NULL */
    if (g_point_ptr_ptr == NULL) {
        printf("Double pointer is NULL\n");
        return -1;
    }

    /* 检查一级指针是否为NULL */
    if (*g_point_ptr_ptr == NULL) {
        printf("Inner pointer is NULL\n");
        return -2;
    }

    /* 访问最终数据并进行条件判断 */
    Point3D* point = *g_point_ptr_ptr;

    /* 分支1: 所有坐标都为正 */
    if (point->x > 0 && point->y > 0 && point->z > 0) {
        printf("All coordinates are positive: (%d, %d, %d)\n",
               point->x, point->y, point->z);
        return point->x + point->y + point->z;
    }
    /* 分支2: 至少一个坐标为负 */
    else if (point->x < 0 || point->y < 0 || point->z < 0) {
        printf("At least one coordinate is negative: (%d, %d, %d)\n",
               point->x, point->y, point->z);
        return -1;
    }
    /* 分支3: 其他情况（有零值） */
    else {
        printf("Some coordinates are zero: (%d, %d, %d)\n",
               point->x, point->y, point->z);
        return 0;
    }
}

int32_t test_array_ptr_condition(void) {
    /* 检查数组指针是否为NULL */
    if (g_int_array_ptr == NULL) {
        return -1;
    }

    /* 假设数组至少有5个元素（硬编码，实际应跟踪大小） */
    /* 分支1: 第一个元素 > 0 */
    if (g_int_array_ptr[0] > 0) {
        /* 进一步检查数组中的其他元素 */
        int32_t sum = 0;
        for (int i = 0; i < 5; i++) {
            sum += g_int_array_ptr[i];
        }

        if (sum > 10) {
            printf("Array sum %d > 10\n", sum);
            return 1;
        } else {
            printf("Array sum %d <= 10\n", sum);
            return 0;
        }
    }
    /* 分支2: 第一个元素 == 0 */
    else if (g_int_array_ptr[0] == 0) {
        printf("First array element is 0\n");
        return -2;
    }
    /* 分支3: 第一个元素 < 0 */
    else {
        printf("First array element is negative: %d\n", g_int_array_ptr[0]);
        return -3;
    }
}

int32_t test_string_ptr_condition(void) {
    /* 检查字符串指针是否为NULL */
    if (g_string_ptr == NULL) {
        printf("String pointer is NULL\n");
        return -1;
    }

    /* 检查字符串是否为空 */
    if (g_string_ptr[0] == '\0') {
        printf("String is empty\n");
        return -2;
    }

    /* 分支1: 字符串以'A'开头 */
    if (g_string_ptr[0] == 'A') {
        printf("String starts with 'A': %s\n", g_string_ptr);
        return 1;
    }
    /* 分支2: 字符串以'B'开头 */
    else if (g_string_ptr[0] == 'B') {
        printf("String starts with 'B': %s\n", g_string_ptr);
        return 2;
    }
    /* 分支3: 字符串包含"test" */
    else if (strstr(g_string_ptr, "test") != NULL) {
        printf("String contains 'test': %s\n", g_string_ptr);
        return 3;
    }
    /* 分支4: 其他情况 */
    else {
        printf("Other string: %s\n", g_string_ptr);
        return 0;
    }
}

int32_t test_multi_ptr_condition(void) {
    /* 复杂条件：多个指针的组合 */

    /* 条件1: g_global_data_ptr不为NULL且enabled为1 */
    int cond1 = (g_global_data_ptr != NULL && g_global_data_ptr->enabled == 1);

    /* 条件2: g_data_container_ptr不为NULL且count > 0 */
    int cond2 = (g_data_container_ptr != NULL && g_data_container_ptr->count > 0);

    /* 条件3: g_int_array_ptr不为NULL且第一个元素 > 0 */
    int cond3 = (g_int_array_ptr != NULL && g_int_array_ptr[0] > 0);

    /* 分支1: 所有条件都满足 */
    if (cond1 && cond2 && cond3) {
        printf("All conditions met\n");
        return 100;
    }
    /* 分支2: 至少两个条件满足 */
    else if ((cond1 && cond2) || (cond1 && cond3) || (cond2 && cond3)) {
        printf("At least two conditions met\n");
        return 50;
    }
    /* 分支3: 至少一个条件满足 */
    else if (cond1 || cond2 || cond3) {
        printf("At least one condition met\n");
        return 10;
    }
    /* 分支4: 没有条件满足 */
    else {
        printf("No conditions met\n");
        return 0;
    }
}

int32_t test_nested_ptr_field(void) {
    /* 检查外层指针 */
    if (g_data_container_ptr == NULL) {
        return -1;
    }

    /* 检查内层指针 */
    if (g_data_container_ptr->data == NULL) {
        return -2;
    }

    GlobalData* data = g_data_container_ptr->data;

    /* 多层嵌套条件 */
    if (g_data_container_ptr->count > 0) {
        if (data->enabled) {
            if (data->value > data->threshold) {
                printf("Nested condition: enabled and value > threshold\n");
                return data->value;
            } else if (data->value == data->threshold) {
                printf("Nested condition: enabled and value == threshold\n");
                return 0;
            } else {
                printf("Nested condition: enabled and value < threshold\n");
                return -data->value;
            }
        } else {
            printf("Data is not enabled\n");
            return -3;
        }
    } else {
        printf("Container is empty\n");
        return -4;
    }
}

int32_t test_ptr_arithmetic_condition(void) {
    if (g_int_array_ptr == NULL) {
        return -1;
    }

    /* 使用指针算术访问不同元素 */
    int32_t* second_elem = g_int_array_ptr + 1;
    int32_t* third_elem = g_int_array_ptr + 2;

    /* 条件基于指针算术结果 */
    if (*second_elem > *g_int_array_ptr) {
        printf("Second element %d > first element %d\n",
               *second_elem, *g_int_array_ptr);

        /* 进一步检查第三个元素 */
        if (*third_elem > *second_elem) {
            printf("Third element %d > second element %d\n",
                   *third_elem, *second_elem);
            return 3;
        } else {
            return 2;
        }
    } else if (*second_elem == *g_int_array_ptr) {
        printf("Second element equals first element: %d\n", *second_elem);
        return 1;
    } else {
        printf("Second element %d < first element %d\n",
               *second_elem, *g_int_array_ptr);
        return 0;
    }
}

int32_t test_ptr_cast_condition(void) {
    /* 模拟void*指针转换 */
    void* void_ptr = (void*)g_global_data_ptr;

    if (void_ptr == NULL) {
        return -1;
    }

    /* 转换回具体类型 */
    GlobalData* casted_ptr = (GlobalData*)void_ptr;

    /* 基于转换后的指针进行条件判断 */
    if (casted_ptr->enabled) {
        if (casted_ptr->status == 'A') {
            printf("Casted pointer: enabled with status A\n");
            return 1;
        } else if (casted_ptr->status == 'B') {
            printf("Casted pointer: enabled with status B\n");
            return 2;
        } else {
            printf("Casted pointer: enabled with other status %c\n",
                   casted_ptr->status);
            return 3;
        }
    } else {
        printf("Casted pointer: not enabled\n");
        return 0;
    }
}