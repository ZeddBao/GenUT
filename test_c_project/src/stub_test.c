#include "stub_test.h"
#include <stdio.h>
#include <string.h>

/* 将被替换的函数实现（打桩目标） */

ConfigData get_configuration(void) {
    ConfigData config = {
        .value = 100,
        .threshold = 50,
        .enabled = true
    };
    printf("get_configuration() called, returning value=%d, threshold=%d, enabled=%d\n",
           config.value, config.threshold, config.enabled);
    return config;
}

int32_t validate_input(int32_t input) {
    printf("validate_input(%d) called\n", input);
    if (input < 0) {
        return -1;
    } else if (input == 0) {
        return 0;
    } else {
        return 1;
    }
}

void process_data(int32_t input, int32_t* output) {
    printf("process_data(%d, output) called\n", input);
    if (output == NULL) {
        return;
    }

    if (input > 100) {
        *output = input * 2;
    } else if (input > 50) {
        *output = input + 10;
    } else {
        *output = input;
    }

    printf("process_data set output to %d\n", *output);
}

int32_t calculate_result(int32_t a, int32_t b) {
    printf("calculate_result(%d, %d) called\n", a, b);
    return a * b - (a + b);
}

bool check_system_status(void) {
    printf("check_system_status() called\n");
    return true;  // 假设系统正常
}

void update_config(ConfigData* config) {
    if (config == NULL) {
        return;
    }

    printf("update_config() called, current value=%d, threshold=%d\n",
           config->value, config->threshold);

    config->value += 10;
    if (config->value > config->threshold) {
        config->enabled = false;
    }

    printf("update_config updated to value=%d, threshold=%d, enabled=%d\n",
           config->value, config->threshold, config->enabled);
}

PointData get_point_data(void) {
    PointData point = {
        .x = 10,
        .y = 20,
        .result = 30
    };
    printf("get_point_data() called, returning x=%d, y=%d, result=%d\n",
           point.x, point.y, point.result);
    return point;
}

int32_t complex_calculation(int32_t a, int32_t b, int32_t c) {
    printf("complex_calculation(%d, %d, %d) called\n", a, b, c);
    return (a * b) + (b * c) - (c * a);
}

/* 测试函数实现 */

int32_t test_branch_on_return_value(int32_t input) {
    printf("test_branch_on_return_value(%d) called\n", input);

    int32_t validation = validate_input(input);

    /* 分支1: 验证失败 */
    if (validation == -1) {
        printf("Validation failed: input negative\n");
        return -1;
    }
    /* 分支2: 输入为零 */
    else if (validation == 0) {
        printf("Input is zero\n");
        return 0;
    }
    /* 分支3: 验证成功 */
    else {
        printf("Validation passed\n");

        /* 进一步处理 */
        int32_t processed;
        process_data(input, &processed);

        if (processed > 100) {
            return processed * 2;
        } else {
            return processed;
        }
    }
}

int32_t test_branch_on_output_param(int32_t input) {
    printf("test_branch_on_output_param(%d) called\n", input);

    int32_t output;
    process_data(input, &output);

    /* 分支1: 处理后的值很大 */
    if (output > 200) {
        printf("Output is large: %d\n", output);
        return output / 2;
    }
    /* 分支2: 处理后的值中等 */
    else if (output > 100) {
        printf("Output is medium: %d\n", output);
        return output + 50;
    }
    /* 分支3: 处理后的值较小 */
    else {
        printf("Output is small: %d\n", output);
        return output * 2;
    }
}

int32_t test_nested_function_conditions(int32_t a, int32_t b) {
    printf("test_nested_function_conditions(%d, %d) called\n", a, b);

    int32_t result1 = calculate_result(a, b);
    bool status = check_system_status();

    /* 嵌套条件：基于多个函数调用 */
    if (status) {
        if (result1 > 0) {
            printf("System OK and result positive: %d\n", result1);

            int32_t result2 = complex_calculation(a, b, result1);
            if (result2 > 100) {
                return result2;
            } else {
                return result1;
            }
        } else if (result1 == 0) {
            printf("System OK but result zero\n");
            return 0;
        } else {
            printf("System OK but result negative: %d\n", result1);
            return -1;
        }
    } else {
        printf("System not OK\n");
        return -100;
    }
}

int32_t test_struct_return_field_condition(void) {
    printf("test_struct_return_field_condition() called\n");

    ConfigData config = get_configuration();

    /* 分支1: 配置启用且值超过阈值 */
    if (config.enabled && config.value > config.threshold) {
        printf("Config enabled and value %d exceeds threshold %d\n",
               config.value, config.threshold);
        return config.value - config.threshold;
    }
    /* 分支2: 配置启用但值未超过阈值 */
    else if (config.enabled) {
        printf("Config enabled but value %d does not exceed threshold %d\n",
               config.value, config.threshold);
        return config.threshold - config.value;
    }
    /* 分支3: 配置禁用 */
    else {
        printf("Config disabled\n");
        return 0;
    }
}

int32_t test_boolean_return_condition(void) {
    printf("test_boolean_return_condition() called\n");

    bool status = check_system_status();

    /* 分支1: 系统正常 */
    if (status) {
        printf("System status is OK\n");

        /* 进一步检查配置 */
        ConfigData config = get_configuration();
        if (config.enabled) {
            return config.value;
        } else {
            return 0;
        }
    }
    /* 分支2: 系统异常 */
    else {
        printf("System status is NOT OK\n");
        return -1;
    }
}

int32_t test_pointer_param_struct_condition(ConfigData* config) {
    printf("test_pointer_param_struct_condition() called\n");

    if (config == NULL) {
        printf("Config pointer is NULL\n");
        return -1;
    }

    printf("Initial config: value=%d, threshold=%d, enabled=%d\n",
           config->value, config->threshold, config->enabled);

    /* 调用函数修改配置 */
    update_config(config);

    printf("Updated config: value=%d, threshold=%d, enabled=%d\n",
           config->value, config->threshold, config->enabled);

    /* 分支基于修改后的配置 */
    if (config->enabled) {
        if (config->value > config->threshold * 2) {
            printf("Config enabled and value greatly exceeds threshold\n");
            return 100;
        } else if (config->value > config->threshold) {
            printf("Config enabled and value exceeds threshold\n");
            return 50;
        } else {
            printf("Config enabled but value does not exceed threshold\n");
            return 10;
        }
    } else {
        printf("Config disabled\n");
        return 0;
    }
}

int32_t test_multi_function_logic(void) {
    printf("test_multi_function_logic() called\n");

    bool status = check_system_status();
    ConfigData config = get_configuration();
    int32_t calc_result = calculate_result(10, 20);

    /* 复杂逻辑组合 */
    if (status && config.enabled) {
        printf("System OK and config enabled\n");

        if (calc_result > 0 || config.value > config.threshold) {
            printf("Either calc positive or value exceeds threshold\n");
            return 1;
        } else {
            printf("Neither condition met\n");
            return 0;
        }
    } else if (status || config.enabled) {
        printf("Either system OK or config enabled\n");
        return -1;
    } else {
        printf("Neither system OK nor config enabled\n");
        return -2;
    }
}

int32_t test_function_in_loop(int32_t* array, int32_t size) {
    printf("test_function_in_loop() called with array size %d\n", size);

    if (array == NULL || size <= 0) {
        return -1;
    }

    int32_t total = 0;
    int32_t count = 0;

    for (int32_t i = 0; i < size; i++) {
        /* 循环中调用函数 */
        int32_t validation = validate_input(array[i]);

        if (validation == 1) {
            /* 验证通过，进行处理 */
            int32_t processed;
            process_data(array[i], &processed);

            total += processed;
            count++;

            /* 循环内条件：处理后的值影响循环行为 */
            if (processed > 100) {
                printf("Element %d processed to large value %d\n", i, processed);
                break;  // 遇到大值提前退出
            }
        } else if (validation == 0) {
            printf("Element %d is zero, skipping\n", i);
        } else {
            printf("Element %d invalid, stopping\n", i);
            return -2;  // 遇到无效值立即返回
        }
    }

    /* 循环后基于函数调用结果分支 */
    if (count == 0) {
        printf("No valid elements processed\n");
        return 0;
    } else if (total > 500) {
        printf("Large total: %d\n", total);
        return total / count;
    } else {
        printf("Normal total: %d\n", total);
        return total;
    }
}

int32_t test_function_in_switch(int32_t input) {
    printf("test_function_in_switch(%d) called\n", input);

    int32_t validation = validate_input(input);

    switch (validation) {
        case -1:
            printf("Switch: Input invalid (negative)\n");
            return -10;

        case 0:
            printf("Switch: Input is zero\n");
            {
                /* case内进一步调用函数 */
                ConfigData config = get_configuration();
                if (config.enabled) {
                    return config.threshold;
                } else {
                    return 0;
                }
            }

        case 1:
            printf("Switch: Input valid\n");
            {
                int32_t processed;
                process_data(input, &processed);

                /* 嵌套switch */
                switch (processed % 3) {
                    case 0:
                        return processed * 2;
                    case 1:
                        return processed + 100;
                    case 2:
                        return processed / 2;
                    default:
                        return processed;
                }
            }

        default:
            printf("Switch: Unexpected validation result\n");
            return -99;
    }
}

int32_t test_function_in_complex_expression(int32_t a, int32_t b, int32_t c) {
    printf("test_function_in_complex_expression(%d, %d, %d) called\n", a, b, c);

    /* 函数调用作为复杂表达式的一部分 */
    int32_t expr_result = (validate_input(a) * calculate_result(b, c))
                         + complex_calculation(a, b, c)
                         - (check_system_status() ? 100 : 0);

    printf("Complex expression result: %d\n", expr_result);

    /* 分支基于表达式结果 */
    if (expr_result > 1000) {
        printf("Very large expression result\n");

        /* 进一步处理 */
        ConfigData config = get_configuration();
        return expr_result + config.value;
    }
    else if (expr_result > 0) {
        printf("Positive expression result\n");
        return expr_result;
    }
    else if (expr_result == 0) {
        printf("Zero expression result\n");
        return 0;
    }
    else {
        printf("Negative expression result\n");
        return -1;
    }
}