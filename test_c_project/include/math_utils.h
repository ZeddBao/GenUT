#ifndef MATH_UTILS_H
#define MATH_UTILS_H

#include <stdint.h>

/**
 * 多分支数学运算函数
 * 根据操作符执行不同的数学运算
 */
typedef enum {
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_DIV,
    OP_MOD,
    OP_POWER,
    OP_SQRT,
    OP_COUNT
} MathOperation;

/**
 * 复杂的数学运算函数，包含多个分支
 */
int32_t math_calculate(int32_t a, int32_t b, MathOperation op);

/**
 * 多层嵌套条件判断的函数
 */
int32_t nested_conditions(int32_t x, int32_t y, int32_t z);

/**
 * 包含复杂逻辑运算符的分支函数
 */
int32_t complex_logic_op(int32_t a, int32_t b, int32_t c, int32_t d);

#endif // MATH_UTILS_H
