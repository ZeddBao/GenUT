/**
 * Function pointer stub test header
 */

#ifndef FUNC_PTR_TEST_H
#define FUNC_PTR_TEST_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*============================================================================
 * Basic functions
 *===========================================================================*/

int add(int a, int b);
int sub(int a, int b);
int mul(int a, int b);
int div_safe(int a, int b);
void print_message(const char* msg);

/*============================================================================
 * Global function pointers
 *===========================================================================*/

extern int (*global_math_op)(int, int);
extern void (*global_printer)(const char*);
extern int (*global_op_array[4])(int, int);

/*============================================================================
 * Struct with function pointer fields
 *===========================================================================*/

typedef struct {
    int (*operation)(int, int);
    void (*logger)(const char*);
    int id;
} MathOperation;

extern MathOperation global_math_op_struct;

/*============================================================================
 * Functions taking function pointers as parameters
 *===========================================================================*/

int compute_with_op(int (*op)(int, int), int x, int y);
int compute_with_math_op(MathOperation* math_op, int x, int y);
void process_with_callback(int value, void (*callback)(const char*));

/*============================================================================
 * Functions returning function pointers
 *===========================================================================*/

int (*get_operation(char op))(int, int);
int (*get_operation_by_index(int index))(int, int);

/*============================================================================
 * Complex test functions
 *===========================================================================*/

int test_global_func_ptr_calls(int a, int b);
int test_func_ptr_param(int (*op)(int, int), int x, int y);
int test_struct_func_ptr(MathOperation* op, int x, int y);
int test_returned_func_ptr(char op, int x, int y);
int test_mixed_func_ptr_sources(int a, int b, char op_char, MathOperation* math_op);
int test_nested_func_ptr_calls(int a, int b);
int test_func_ptr_in_condition(int a, int b, int (*op1)(int, int), int (*op2)(int, int));

/*============================================================================
 * Main test function
 *===========================================================================*/

int main_func_ptr_test(void);

#ifdef __cplusplus
}
#endif

#endif /* FUNC_PTR_TEST_H */