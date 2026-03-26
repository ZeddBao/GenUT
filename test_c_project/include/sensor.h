#ifndef SENSOR_H
#define SENSOR_H

#include <stdint.h>

typedef struct {
    int32_t temperature;
    int32_t humidity;
    uint8_t is_valid;
} SensorReading;

typedef struct {
    int32_t min_temp;
    int32_t max_temp;
} SensorConfig;

/* 结构体值传参：根据字段条件分支 */
int32_t validate_reading(SensorReading reading, SensorConfig config);

/* 结构体指针传参：根据 -> 字段条件分支 */
int32_t process_reading(SensorReading* reading);

#endif // SENSOR_H
