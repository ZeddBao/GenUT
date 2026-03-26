#include "sensor.h"

int32_t validate_reading(SensorReading reading, SensorConfig config) {
    if (reading.is_valid == 0) {
        return -1;
    }
    if (reading.temperature < config.min_temp) {
        return -2;
    }
    if (reading.temperature > config.max_temp) {
        return -3;
    }
    if (reading.humidity < 0) {
        return -4;
    }
    if (reading.humidity > 100) {
        return -5;
    }
    return 0;
}

int32_t process_reading(SensorReading* reading) {
    if (reading == NULL) {
        return -1;
    }
    if (reading->temperature > 100) {
        reading->is_valid = 0;
        return -2;
    }
    if (reading->humidity > 80) {
        return 1;
    }
    return 0;
}
