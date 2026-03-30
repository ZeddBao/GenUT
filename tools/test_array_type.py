#!/usr/bin/env python3
"""Test libclang array type extraction."""

import os
import sys
import clang.cindex as clang

def main():
    source_file = os.path.realpath('test_c_project/src/basic_functions.c')
    compile_args = ['-I', 'test_c_project/include']

    index = clang.Index.create()
    tu = index.parse(source_file, args=compile_args)

    for node in tu.cursor.walk_preorder():
        if node.kind == clang.CursorKind.FUNCTION_DECL:
            if node.location.file and os.path.realpath(node.location.file.name) == source_file:
                if node.is_definition():
                    func_name = node.spelling
                    if func_name == 'fixed_array_function':
                        print(f"Function: {func_name}")
                        print(f"  Return type: {node.result_type.spelling}")
                        print(f"  Return type kind: {node.result_type.kind}")
                        for arg in node.get_arguments():
                            param_name = arg.spelling
                            print(f"\n  Parameter: {param_name}")
                            print(f"    Type spelling: '{arg.type.spelling}'")
                            print(f"    Type kind: {arg.type.kind}")
                            print(f"    Type kind name: {str(arg.type.kind)}")
                            print(f"    Canonical spelling: '{arg.type.get_canonical().spelling}'")
                            print(f"    Canonical kind: {arg.type.get_canonical().kind}")

                            # Check if it's an array type
                            print(f"    Is array type: {arg.type.kind == clang.TypeKind.CONSTANTARRAY}")
                            print(f"    Is incomplete array: {arg.type.kind == clang.TypeKind.INCOMPLETEARRAY}")
                            print(f"    Is variable array: {arg.type.kind == clang.TypeKind.VARIABLEARRAY}")
                            print(f"    Is dependent sized array: {arg.type.kind == clang.TypeKind.DEPENDENTSIZEDARRAY}")

                            # Get array element type and size
                            if arg.type.kind == clang.TypeKind.CONSTANTARRAY:
                                print(f"    Array size: {arg.type.element_count}")
                                print(f"    Element type: {arg.type.element_type.spelling}")

                            # Check if it's a pointer type (arrays decay to pointers)
                            print(f"    Is pointer type: {arg.type.kind == clang.TypeKind.POINTER}")

                            # Try to get tokens
                            try:
                                tokens = list(arg.get_tokens())
                                if tokens:
                                    print(f"    Tokens: {[t.spelling for t in tokens]}")
                            except:
                                pass
                        break

if __name__ == '__main__':
    main()