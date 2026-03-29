#!/usr/bin/env python3
"""Analyze function pointer AST representation with libclang."""

import clang.cindex as clang
import sys
import os

def print_node(node, indent=0):
    """Print node information."""
    prefix = "  " * indent
    kind_name = str(node.kind).replace('CursorKind.', '')

    # Get type information
    type_info = ""
    if node.type.kind != clang.TypeKind.INVALID:
        type_kind = str(node.type.kind).replace('TypeKind.', '')
        type_spelling = node.type.spelling
        type_info = f" type={type_kind}:'{type_spelling}'"

    # Get referenced declaration if any
    ref_info = ""
    if node.referenced:
        ref_kind = str(node.referenced.kind).replace('CursorKind.', '')
        ref_info = f" ref->{ref_kind}:'{node.referenced.spelling}'"

    tokens = [t.spelling for t in node.get_tokens()]
    token_str = f" tokens={' '.join(tokens)}" if tokens else ""

    print(f"{prefix}{kind_name}: '{node.spelling}'{type_info}{ref_info}{token_str}")

    # Print children
    for child in node.get_children():
        print_node(child, indent + 1)

def analyze_file(filename):
    """Analyze C file for function pointers."""
    print(f"Analyzing {filename}")
    print("=" * 80)

    # Set libclang path if needed
    # clang.Config.set_library_path("/path/to/libclang")

    index = clang.Index.create()
    tu = index.parse(filename)

    # Walk through all nodes
    for node in tu.cursor.walk_preorder():
        if node.kind == clang.CursorKind.CALL_EXPR:
            print("\n=== CALL_EXPR ===")
            print_node(node)

            # Check if this is a function pointer call
            children = list(node.get_children())
            if children:
                callee = children[0]
                print(f"\nCallee expression kind: {callee.kind}")
                print(f"Callee type: {callee.type.kind}")
                print(f"Callee type spelling: {callee.type.spelling}")

                # Check if callee is a function pointer
                if callee.type.kind == clang.TypeKind.POINTER:
                    pointee = callee.type.get_pointee()
                    print(f"Pointee type: {pointee.kind}")
                    print(f"Pointee spelling: {pointee.spelling}")

                    if pointee.kind == clang.TypeKind.FUNCTIONPROTO:
                        print(">>> This is a function pointer call!")
                        # Get function prototype info
                        print(f"Result type: {pointee.get_result().spelling}")

                        # Try to get argument types
                        try:
                            for i, arg_type in enumerate(pointee.argument_types()):
                                print(f"  Arg {i}: {arg_type.spelling}")
                        except:
                            print("  Could not get argument types")

        elif node.kind == clang.CursorKind.VAR_DECL:
            # Check for function pointer variable declarations
            if node.type.kind == clang.TypeKind.POINTER:
                pointee = node.type.get_pointee()
                if pointee.kind == clang.TypeKind.FUNCTIONPROTO:
                    print(f"\n=== FUNCTION POINTER VARIABLE: {node.spelling} ===")
                    print_node(node)

        elif node.kind == clang.CursorKind.FUNCTION_DECL:
            # Check function parameters for function pointers
            for child in node.get_children():
                if child.kind == clang.CursorKind.PARM_DECL:
                    if child.type.kind == clang.TypeKind.POINTER:
                        pointee = child.type.get_pointee()
                        if pointee.kind == clang.TypeKind.FUNCTIONPROTO:
                            print(f"\n=== FUNCTION POINTER PARAMETER in {node.spelling}: {child.spelling} ===")
                            print_node(child)

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Use the test file
        filename = "test_c_project/src/temp_func_ptr.c"

    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return 1

    analyze_file(filename)
    return 0

if __name__ == "__main__":
    sys.exit(main())