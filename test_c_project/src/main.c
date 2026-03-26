#include "math_utils.h"
#include "data_processor.h"
#include "state_machine.h"
#include <stdio.h>

int main(void) {
    printf("=== Test C Project Demo ===\n\n");

    // 测试 math_calculate
    printf("Testing math_calculate:\n");
    printf("  10 + 5 = %d\n", math_calculate(10, 5, OP_ADD));
    printf("  10 - 5 = %d\n", math_calculate(10, 5, OP_SUB));
    printf("  10 * 5 = %d\n", math_calculate(10, 5, OP_MUL));
    printf("  10 / 5 = %d\n", math_calculate(10, 5, OP_DIV));
    printf("  10 mod 3 = %d\n", math_calculate(10, 3, OP_MOD));
    printf("  2^5 = %d\n", math_calculate(2, 5, OP_POWER));
    printf("  sqrt(16) = %d\n", math_calculate(16, 0, OP_SQRT));

    // 测试 nested_conditions
    printf("\nTesting nested_conditions:\n");
    printf("  (1, 1, 1) = %d\n", nested_conditions(1, 1, 1));
    printf("  (0, 0, 0) = %d\n", nested_conditions(0, 0, 0));
    printf("  (-1, -1, -1) = %d\n", nested_conditions(-1, -1, -1));

    // 测试 data_buffer
    printf("\nTesting DataBuffer:\n");
    DataBuffer buffer;
    data_buffer_init(&buffer);

    for (int32_t i = 1; i <= 12; i++) {
        data_buffer_add(&buffer, i * 10);
    }

    int32_t result = data_buffer_process(&buffer);
    printf("  Process result: %d\n", result);

    // 测试 state_machine
    printf("\nTesting State Machine:\n");
    system_init();
    printf("  Initial state: %d\n", get_system_state());

    state_machine_handle_event(EVENT_POWER_ON);
    printf("  After POWER_ON: %d\n", get_system_state());

    state_machine_handle_event(EVENT_START);
    printf("  After START: %d\n", get_system_state());

    state_machine_handle_event(EVENT_SUSPEND);
    printf("  After SUSPEND: %d\n", get_system_state());

    state_machine_handle_event(EVENT_RESUME);
    printf("  After RESUME: %d\n", get_system_state());

    state_machine_handle_event(EVENT_POWER_OFF);
    printf("  After POWER_OFF: %d\n", get_system_state());

    printf("\n=== Demo Complete ===\n");
    return 0;
}
