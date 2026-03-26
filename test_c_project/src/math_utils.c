#include "math_utils.h"
#include <math.h>
#include <stdio.h>

int32_t math_calculate(int32_t a, int32_t b, MathOperation op) {
    switch (op) {
        case OP_ADD:
            return a + b;
        case OP_SUB:
            return a - b;
        case OP_MUL:
            return a * b;
        case OP_DIV:
            if (b == 0) {
                printf("Error: Division by zero\n");
                return 0;
            }
            return a / b;
        case OP_MOD:
            if (b == 0) {
                printf("Error: Modulo by zero\n");
                return 0;
            }
            return a % b;
        case OP_POWER:
            if (b < 0) {
                printf("Error: Negative exponent not supported\n");
                return 0;
            }
            return (int32_t)pow(a, b);
        case OP_SQRT:
            if (a < 0) {
                printf("Error: Square root of negative number\n");
                return 0;
            }
            return (int32_t)sqrt(a);
        default:
            printf("Error: Unknown operation\n");
            return 0;
    }
}

int32_t nested_conditions(int32_t x, int32_t y, int32_t z) {
    // 多层嵌套的if-else分支
    if (x > 0) {
        if (y > 0) {
            if (z > 0) {
                return x + y + z;
            } else if (z == 0) {
                return x + y;
            } else {
                return x - y + z;
            }
        } else if (y == 0) {
            if (z > 0) {
                return x + z;
            } else if (z == 0) {
                return x;
            } else {
                return x - z;
            }
        } else {
            if (z > 0) {
                return x - y + z;
            } else if (z == 0) {
                return x - y;
            } else {
                return x - y - z;
            }
        }
    } else if (x == 0) {
        if (y > 0) {
            if (z > 0) {
                return y + z;
            } else if (z == 0) {
                return y;
            } else {
                return y - z;
            }
        } else if (y == 0) {
            if (z > 0) {
                return z;
            } else if (z == 0) {
                return 0;
            } else {
                return -z;
            }
        } else {
            if (z > 0) {
                return -y + z;
            } else if (z == 0) {
                return -y;
            } else {
                return -y - z;
            }
        }
    } else {
        if (y > 0) {
            if (z > 0) {
                return -x + y + z;
            } else if (z == 0) {
                return -x + y;
            } else {
                return -x + y - z;
            }
        } else if (y == 0) {
            if (z > 0) {
                return -x + z;
            } else if (z == 0) {
                return -x;
            } else {
                return -x - z;
            }
        } else {
            if (z > 0) {
                return -x - y + z;
            } else if (z == 0) {
                return -x - y;
            } else {
                return -x - y - z;
            }
        }
    }
}

int32_t complex_logic_op(int32_t a, int32_t b, int32_t c, int32_t d) {
    // 复杂的逻辑运算符分支
    if (a > 0 && b > 0) {
        if (c > 0 && d > 0) {
            return a * b * c * d;
        } else if (c > 0 || d > 0) {
            return a * b * (c + d);
        } else {
            return a * b;
        }
    } else if (a > 0 || b > 0) {
        if (c > 0 && d > 0) {
            return (a + b) * c * d;
        } else if (c > 0 || d > 0) {
            return (a + b) * (c + d);
        } else {
            return a + b;
        }
    } else {
        if (c > 0 && d > 0) {
            return c * d;
        } else if (c > 0 || d > 0) {
            return c + d;
        } else {
            return 0;
        }
    }
}
