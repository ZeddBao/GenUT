#include "data_processor.h"
#include <stdio.h>

void data_buffer_init(DataBuffer* buffer) {
    buffer->count = 0;
    buffer->capacity = MAX_BUFFER_SIZE;
    buffer->state = PROCESS_IDLE;
}

int32_t data_buffer_add(DataBuffer* buffer, int32_t value) {
    if (buffer->count >= buffer->capacity) {
        printf("Error: Buffer is full\n");
        return -1;
    }

    buffer->data[buffer->count] = value;
    buffer->count++;

    // 需要添加10个数据后才能进入激活状态
    if (buffer->count >= 10) {
        buffer->state = PROCESS_ACTIVE;
        printf("Buffer reached active state with %d elements\n", buffer->count);
    } else if (buffer->count == 5) {
        printf("Buffer is warming up with %d elements\n", buffer->count);
    } else {
        buffer->state = PROCESS_IDLE;
    }

    return buffer->count;
}

int32_t data_buffer_process(DataBuffer* buffer) {
    if (buffer->state == PROCESS_IDLE || buffer->state == PROCESS_ERROR) {
        printf("Error: Cannot process in current state\n");
        return -1;
    }

    if (buffer->count == 0) {
        printf("Error: Empty buffer\n");
        buffer->state = PROCESS_ERROR;
        return -1;
    }

    int32_t sum = 0;
    int32_t min = buffer->data[0];
    int32_t max = buffer->data[0];
    int32_t result;

    // 循环处理所有数据
    for (uint32_t i = 0; i < buffer->count; i++) {
        sum += buffer->data[i];
        if (buffer->data[i] < min) {
            min = buffer->data[i];
        }
        if (buffer->data[i] > max) {
            max = buffer->data[i];
        }
    }

    int32_t avg = sum / (int32_t)buffer->count;

    // 根据元素数量进入不同分支
    if (buffer->count >= 100) {
        printf("Processing large dataset (%d elements)\n", buffer->count);
        result = avg * 2 + min + max;
    } else if (buffer->count >= 50) {
        printf("Processing medium dataset (%d elements)\n", buffer->count);
        result = avg + (min + max) / 2;
    } else if (buffer->count >= 20) {
        printf("Processing small dataset (%d elements)\n", buffer->count);
        result = avg;
    } else {
        printf("Processing tiny dataset (%d elements)\n", buffer->count);
        result = min + max;
    }

    buffer->state = PROCESS_COMPLETED;
    return result;
}

int32_t complex_loop_processor(int32_t* array, uint32_t size, int32_t threshold) {
    if (array == NULL || size == 0) {
        printf("Error: Invalid input\n");
        return -1;
    }

    int32_t count = 0;
    int32_t result = 0;

    // 外层循环
    for (uint32_t i = 0; i < size; i++) {
        if (array[i] > threshold) {
            // 进入特定分支需要满足条件
            int32_t temp = 1;
            // 内层循环，需要迭代5次才能进入
            for (int32_t j = 0; j < array[i] % 10; j++) {
                temp *= 2;
                if (j >= 5) {
                    // 只有当内层循环执行超过5次才进入此分支
                    result += array[i] * temp;
                    count++;
                }
            }

            // 另一个需要循环满足条件的分支
            int32_t sum = 0;
            for (uint32_t k = 0; k < size; k++) {
                sum += array[k];
                if (sum > 1000) {
                    // 只有当累加超过1000才进入
                    result += sum;
                    break;
                }
            }
        } else if (array[i] < -threshold) {
            // 负值处理分支
            int32_t abs_val = -array[i];
            for (int32_t j = 0; j < 3; j++) {
                abs_val /= 2;
            }
            result -= abs_val;
        } else {
            // 在阈值范围内的值
            result += array[i];
        }
    }

    // 根据计数结果进入不同分支
    if (count > 10) {
        result = result * count;
    } else if (count > 5) {
        result = result + count * 10;
    } else if (count > 0) {
        result = result + count;
    }

    return result;
}

void bubble_sort(int32_t* array, uint32_t size) {
    if (array == NULL || size <= 1) {
        return;
    }

    for (uint32_t i = 0; i < size - 1; i++) {
        int32_t swapped = 0;
        for (uint32_t j = 0; j < size - i - 1; j++) {
            if (array[j] > array[j + 1]) {
                // 交换
                int32_t temp = array[j];
                array[j] = array[j + 1];
                array[j + 1] = temp;
                swapped = 1;
            }
        }
        // 如果没有发生交换，提前退出
        if (!swapped) {
            break;
        }
    }
}
