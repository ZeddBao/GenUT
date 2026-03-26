#include "state_machine.h"
#include <stdio.h>

// 全局系统上下文
SystemContext g_system_context;

SystemState get_system_state(void) {
    return g_system_context.state;
}

int32_t check_emergency_stop(void) {
    // 检查是否需要紧急停止
    if (g_system_context.config.temperature > 100) {
        return 1;  // 需要紧急停止
    } else if (g_system_context.config.pressure > 500) {
        return 1;  // 需要紧急停止
    } else if (g_system_context.error_count > 3) {
        return 1;  // 需要紧急停止
    } else if (g_system_context.error_code != 0) {
        return 2;  // 需要进入错误状态
    }
    return 0;  // 正常
}

int32_t check_temperature_safe(int32_t temp) {
    if (temp < -20) {
        return -1;  // 温度过低
    } else if (temp > 80) {
        return 1;   // 温度过高
    } else if (temp < 0) {
        return 0;   // 温度偏低但安全
    } else if (temp > 60) {
        return 2;   // 温度偏高但安全
    }
    return 0;  // 温度正常
}

SystemState transition_state(SystemState current, SystemEvent event) {
    // 根据当前状态和事件决定下一个状态
    switch (current) {
        case SYSTEM_OFF:
            if (event == EVENT_POWER_ON) {
                return SYSTEM_STANDBY;
            }
            break;

        case SYSTEM_STANDBY:
            switch (event) {
                case EVENT_START:
                    // 检查温度是否安全，函数返回值决定分支
                    int32_t temp_check = check_temperature_safe(g_system_context.config.temperature);
                    if (temp_check == 1) {
                        printf("Warning: Temperature too high, cannot start\n");
                        return SYSTEM_STANDBY;
                    } else if (temp_check == -1) {
                        printf("Warning: Temperature too low, cannot start\n");
                        return SYSTEM_STANDBY;
                    } else if (temp_check == 2) {
                        printf("Warning: Temperature elevated, starting with caution\n");
                        return SYSTEM_RUNNING;
                    } else {
                        return SYSTEM_RUNNING;
                    }
                case EVENT_POWER_OFF:
                    return SYSTEM_OFF;
                default:
                    break;
            }
            break;

        case SYSTEM_RUNNING:
            switch (event) {
                case EVENT_SUSPEND:
                    return SYSTEM_SUSPENDED;
                case EVENT_ERROR:
                    return SYSTEM_ERROR;
                case EVENT_POWER_OFF:
                    return SYSTEM_SHUTDOWN;
                case EVENT_POWER_ON:
                    return SYSTEM_RUNNING;
                default:
                    break;
            }
            break;

        case SYSTEM_SUSPENDED:
            switch (event) {
                case EVENT_RESUME:
                    // 根据全局配置决定是否可以恢复
                    if (g_system_context.config.uptime > 3600) {
                        printf("Warning: System uptime too long, requires reset\n");
                        return SYSTEM_ERROR;
                    }
                    return SYSTEM_RUNNING;
                case EVENT_RESET:
                    system_reset();
                    return SYSTEM_STANDBY;
                case EVENT_POWER_OFF:
                    return SYSTEM_SHUTDOWN;
                default:
                    break;
            }
            break;

        case SYSTEM_ERROR:
            switch (event) {
                case EVENT_RESET:
                    // 根据错误代码决定处理方式
                    if (g_system_context.error_code >= 100) {
                        printf("Critical error, full reset required\n");
                        system_reset();
                        return SYSTEM_OFF;
                    } else if (g_system_context.error_code >= 50) {
                        printf("Major error, partial reset\n");
                        g_system_context.error_code = 0;
                        return SYSTEM_STANDBY;
                    } else {
                        printf("Minor error, clear and continue\n");
                        g_system_context.error_code = 0;
                        g_system_context.error_count = 0;
                        return SYSTEM_RUNNING;
                    }
                case EVENT_POWER_OFF:
                    return SYSTEM_SHUTDOWN;
                default:
                    break;
            }
            break;

        case SYSTEM_SHUTDOWN:
            // 只能通过 power_on 重新启动
            if (event == EVENT_POWER_ON) {
                system_reset();
                return SYSTEM_OFF;
            }
            break;

        default:
            break;
    }

    return current;  // 默认保持当前状态
}

SystemState state_machine_handle_event(SystemEvent event) {
    // 检查紧急停止
    int32_t emergency = check_emergency_stop();
    if (emergency == 1) {
        printf("EMERGENCY STOP triggered!\n");
        g_system_context.state = SYSTEM_ERROR;
        g_system_context.error_code = 999;
        g_system_context.error_count++;
        return SYSTEM_ERROR;
    } else if (emergency == 2) {
        printf("Non-critical error detected\n");
        g_system_context.state = SYSTEM_ERROR;
        return SYSTEM_ERROR;
    }

    // 正常状态转换
    SystemState new_state = transition_state(g_system_context.state, event);

    // 记录状态变化
    if (new_state != g_system_context.state) {
        printf("State transition: %d -> %d\n", g_system_context.state, new_state);
        g_system_context.state = new_state;
    }

    return new_state;
}

void handle_fault(int32_t error_code) {
    g_system_context.error_code = error_code;
    g_system_context.error_count++;

    // 根据错误代码进入不同分支
    if (error_code >= 200) {
        printf("Critical fault: %d\n", error_code);
        g_system_context.state = SYSTEM_ERROR;
    } else if (error_code >= 100) {
        printf("Major fault: %d\n", error_code);
        g_system_context.state = SYSTEM_ERROR;
    } else if (error_code >= 50) {
        printf("Minor fault: %d\n", error_code);
        // 根据全局状态决定处理
        if (g_system_context.state == SYSTEM_RUNNING) {
            g_system_context.state = SYSTEM_ERROR;
        }
    } else if (error_code > 0) {
        printf("Warning: %d\n", error_code);
        // 警告级别，不改变状态
    } else {
        printf("Info: No error\n");
    }
}

void system_init(void) {
    g_system_context.state = SYSTEM_OFF;
    g_system_context.config.temperature = 25;
    g_system_context.config.pressure = 100;
    g_system_context.config.humidity = 50;
    g_system_context.config.uptime = 0;
    g_system_context.error_code = 0;
    g_system_context.error_count = 0;
    printf("System initialized\n");
}

void system_reset(void) {
    g_system_context.config.temperature = 25;
    g_system_context.config.pressure = 100;
    g_system_context.config.humidity = 50;
    g_system_context.config.uptime = 0;
    g_system_context.error_code = 0;
    g_system_context.error_count = 0;
    g_system_context.state = SYSTEM_STANDBY;
    printf("System reset\n");
}
