
#ifndef DATA_PROCESSOR_H
#define DATA_PROCESSOR_H

#include <stdint.h>

#define MAX_BUFFER_SIZE 1024

/**
 * 数据处理状态枚举
 */
typedef enum {
    PROCESS_IDLE,
    PROCESS_ACTIVE,
    PROCESS_COMPLETED,
    PROCESS_ERROR,
    PROCESS_COUNT
} ProcessState;

/**
 * 数据缓冲区结构
 */
typedef struct {
    int32_t data[MAX_BUFFER_SIZE];
    uint32_t count;
    uint32_t capacity;
    ProcessState state;
} DataBuffer;

/**
 * 初始化数据缓冲区
 */
void data_buffer_init(DataBuffer* buffer);

/**
 * 向缓冲区添加数据
 * 需要循环达到一定次数才能进入特定分支
 */
int32_t data_buffer_add(DataBuffer* buffer, int32_t value);

/**
 * 处理缓冲区数据
 * 包含循环和条件分支
 */
int32_t data_buffer_process(DataBuffer* buffer);

/**
 * 复杂的循环处理函数
 * 需要满足一定条件才能进入内部循环分支
 */
int32_t complex_loop_processor(int32_t* array, uint32_t size, int32_t threshold);

/**
 * 多重嵌套循环的排序函数
 */
void bubble_sort(int32_t* array, uint32_t size);

#endif // DATA_PROCESSOR_H
