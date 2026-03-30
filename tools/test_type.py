#!/usr/bin/env python3
"""Test libclang type extraction for typedef parameters."""

import os
import sys
import clang.cindex as clang

def main():
    # Use the same compile commands as gen_ut
    source_file = os.path.realpath('test_c_project/src/basic_functions.c')
    compile_db = os.path.realpath('test_c_project/compile_commands.json')

    # Parse compile commands (simplified)
    compile_args = ['-I', 'test_c_project/include']

    index = clang.Index.create()
    tu = index.parse(source_file, args=compile_args)

    for node in tu.cursor.walk_preorder():
        if node.kind == clang.CursorKind.FUNCTION_DECL:
            if node.location.file and os.path.realpath(node.location.file.name) == source_file:
                if node.is_definition():
                    func_name = node.spelling
                    if func_name == 'struct_by_value_function':
                        print(f"Function: {func_name}")
                        print(f"  Return type: {node.result_type.spelling}")
                        for arg in node.get_arguments():
                            param_name = arg.spelling
                            print(f"\n  Parameter: {param_name}")
                            print(f"    Type spelling: '{arg.type.spelling}'")
                            print(f"    Type kind: {arg.type.kind}")
                            print(f"    Type kind name: {str(arg.type.kind)}")
                            print(f"    Canonical spelling: '{arg.type.get_canonical().spelling}'")
                            print(f"    Canonical kind: {arg.type.get_canonical().kind}")

                            # Try to get typedef info
                            try:
                                decl = arg.type.get_declaration()
                                if decl:
                                    print(f"    Type declaration: {decl.spelling}, kind: {decl.kind}")
                                    if decl.kind == clang.CursorKind.TYPEDEF_DECL:
                                        print(f"    Typedef name: {decl.spelling}")
                                        print(f"    Underlying type: {decl.underlying_typedef_type.spelling if decl.underlying_typedef_type else 'None'}")
                            except Exception as e:
                                print(f"    Error getting declaration: {e}")

                            # Try get_named_type if exists
                            if hasattr(arg.type, 'get_named_type'):
                                try:
                                    named = arg.type.get_named_type()
                                    print(f"    Named type: {named.spelling}")
                                except:
                                    pass

                            # Try to get the original type from the cursor's tokens
                            try:
                                tokens = list(arg.get_tokens())
                                if tokens:
                                    print(f"    Tokens: {[t.spelling for t in tokens]}")
                            except:
                                pass
                        break

if __name__ == '__main__':
    main()