#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

#include <stdint.h>

/**
 * 全局系统状态
 */
typedef enum {
    SYSTEM_OFF,
    SYSTEM_STANDBY,
    SYSTEM_RUNNING,
    SYSTEM_SUSPENDED,
    SYSTEM_ERROR,
    SYSTEM_SHUTDOWN,
    SYSTEM_STATE_COUNT
} SystemState;

/**
 * 系统事件枚举
 */
typedef enum {
    EVENT_POWER_ON,
    EVENT_START,
    EVENT_SUSPEND,
    EVENT_RESUME,
    EVENT_ERROR,
    EVENT_RESET,
    EVENT_POWER_OFF,
    EVENT_COUNT
} SystemEvent;

/**
 * 系统配置结构
 */
typedef struct {
    int32_t temperature;
    int32_t pressure;
    int32_t humidity;
    uint32_t uptime;
} SystemConfig;

/**
 * 系统上下文结构
 */
typedef struct {
    SystemState state;
    SystemConfig config;
    int32_t error_code;
    uint32_t error_count;
} SystemContext;

/**
 * 全局系统上下文 (外部可见)
 */
extern SystemContext g_system_context;

/**
 * 获取系统状态
 * 用于测试函数返回值分支
 */
SystemState get_system_state(void);

/**
 * 检查系统是否需要紧急停止
 * 函数返回值控制分支
 */
int32_t check_emergency_stop(void);

/**
 * 检查温度是否在安全范围内
 * 函数返回值控制分支
 */
int32_t check_temperature_safe(int32_t temp);

/**
 * 根据全局状态和函数返回值处理事件
 * 复杂的状态机，包含全局变量和函数返回值分支
 */
SystemState state_machine_handle_event(SystemEvent event);

/**
 * 系统状态转换函数
 * 需要根据当前状态和全局配置决定
 */
SystemState transition_state(SystemState current, SystemEvent event);

/**
 * 系统故障处理函数
 * 根据错误代码进入不同分支
 */
void handle_fault(int32_t error_code);

/**
 * 系统初始化
 */
void system_init(void);

/**
 * 系统重置
 */
void system_reset(void);

#endif // STATE_MACHINE_H
