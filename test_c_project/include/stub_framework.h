/**
 * @file stub_framework.h
 * @brief Runtime hot-patch stub framework for unit testing
 *
 * Stubs regular C functions at runtime by overwriting the first 5 bytes of the
 * target function with a relative JMP to a replacement function.  Both the
 * target and the stub must reside within ±2 GB of each other (guaranteed for
 * functions in the same executable image).
 *
 * Usage within a TEST_F body:
 *
 *   INSTALL_STUB(dep_query_int, my_stub);
 *   int result = function_under_test();
 *   EXPECT_EQ(result, expected);
 *   UNINSTALL_STUB(dep_query_int);
 *
 * INSTALL_STUB declares a local _StubCtx variable on the stack; UNINSTALL_STUB
 * references the same variable — both macros must be used in the same scope.
 *
 * For stubs of function-pointer *variables* (not patched functions) use:
 *   INSTALL_FUNC_PTR_STUB(var, stub_fn);
 */

#ifndef STUB_FRAMEWORK_H
#define STUB_FRAMEWORK_H

#include <stdint.h>
#include <string.h>

#ifdef _WIN32
#  include <windows.h>
#else
#  include <sys/mman.h>
#  include <unistd.h>
#endif

/* Size of the x86 / x86-64 near JMP instruction: opcode (0xE9) + 4-byte rel32 */
#define _STUB_JMP_SIZE 5

typedef struct {
    void    *target;
    uint8_t  saved[_STUB_JMP_SIZE];
} _StubCtx;

/**
 * Overwrite the first _STUB_JMP_SIZE bytes of `target` with a JMP to
 * `replacement` after saving the original bytes into `ctx`.
 */
static inline void _stub_install(_StubCtx *ctx, void *target, void *replacement)
{
    ctx->target = target;
    memcpy(ctx->saved, target, _STUB_JMP_SIZE);

    uint8_t jmp[_STUB_JMP_SIZE];
    jmp[0] = 0xE9;  /* JMP rel32 */
    int32_t rel = (int32_t)((uint8_t *)replacement - (uint8_t *)target - _STUB_JMP_SIZE);
    memcpy(jmp + 1, &rel, sizeof(rel));

#ifdef _WIN32
    DWORD old_protect;
    VirtualProtect(target, _STUB_JMP_SIZE, PAGE_EXECUTE_READWRITE, &old_protect);
    memcpy(target, jmp, _STUB_JMP_SIZE);
    VirtualProtect(target, _STUB_JMP_SIZE, old_protect, &old_protect);
#else
    long   page_size  = sysconf(_SC_PAGESIZE);
    void  *page_start = (void *)((uintptr_t)target & ~(uintptr_t)(page_size - 1));
    mprotect(page_start, (size_t)page_size, PROT_READ | PROT_WRITE | PROT_EXEC);
    memcpy(target, jmp, _STUB_JMP_SIZE);
    mprotect(page_start, (size_t)page_size, PROT_READ | PROT_EXEC);
#endif
}

/** Restore the original bytes saved by _stub_install. */
static inline void _stub_restore(_StubCtx *ctx)
{
#ifdef _WIN32
    DWORD old_protect;
    VirtualProtect(ctx->target, _STUB_JMP_SIZE, PAGE_EXECUTE_READWRITE, &old_protect);
    memcpy(ctx->target, ctx->saved, _STUB_JMP_SIZE);
    VirtualProtect(ctx->target, _STUB_JMP_SIZE, old_protect, &old_protect);
#else
    long   page_size  = sysconf(_SC_PAGESIZE);
    void  *page_start = (void *)((uintptr_t)ctx->target & ~(uintptr_t)(page_size - 1));
    mprotect(page_start, (size_t)page_size, PROT_READ | PROT_WRITE | PROT_EXEC);
    memcpy(ctx->target, ctx->saved, _STUB_JMP_SIZE);
    mprotect(page_start, (size_t)page_size, PROT_READ | PROT_EXEC);
#endif
}

/**
 * Install a hot-patch stub on a regular C function.
 *
 * Declares a stack variable `_sctx_<func>` in the current scope that holds
 * the saved bytes; UNINSTALL_STUB must be called in the same scope to restore.
 *
 * @param func  Name of the C function to patch (must have external linkage).
 * @param stub  Replacement function with the same signature.
 */
#define INSTALL_STUB(func, stub)                                        \
    _StubCtx _sctx_##func;                                              \
    _stub_install(&_sctx_##func, (void *)(func), (void *)(stub))

/**
 * Restore a hot-patched function to its original code.
 * Must be called in the same scope as the matching INSTALL_STUB.
 *
 * @param func  Same function name passed to INSTALL_STUB.
 */
#define UNINSTALL_STUB(func)                                            \
    _stub_restore(&_sctx_##func)

/**
 * Assign a stub function to a function-pointer variable.
 * Does NOT perform hot patching — suitable for global/struct function pointers
 * that are already indirected through a variable.
 *
 * @param var   Function-pointer variable to overwrite.
 * @param stub  Replacement function.
 */
#define INSTALL_FUNC_PTR_STUB(var, stub)  ((var) = (stub))

#endif /* STUB_FRAMEWORK_H */
