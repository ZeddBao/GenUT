"""GTest builder with configurable naming and default values."""

import os
import re

from .models import PathConstraint, FunctionInfo
from .config import GeneratorConfig


class GTestBuilder:
    """Responsible for generating GTest framework code with configurable naming and defaults."""

    def __init__(self, source_file, funcs_info, known_constants,
                 config: GeneratorConfig, outdir=None, project_includes=None, construct=False,
                 stub_framework=None, stub_builder=None):
        self.source_file = source_file
        self.funcs_info = funcs_info
        self.known_constants = known_constants
        self.project_includes = project_includes or []
        self.construct = construct
        self.config = config
        self.stub_framework = stub_framework  # StubFrameworkBase instance or None
        self.stub_builder = stub_builder      # StubBuilder instance or None

        # Resolve output paths using naming configuration
        self._resolve_output_paths(outdir)

    def _resolve_output_paths(self, outdir):
        """Resolve output file paths using naming configuration."""
        out_dir = os.path.abspath(outdir) if outdir else os.path.dirname(os.path.abspath(self.source_file))
        base_name = os.path.splitext(os.path.basename(self.source_file))[0]
        naming = self.config.naming

        self.out_base_name = f"{naming.file_prefix}{base_name}{naming.file_suffix}"
        self.test_suite_name = self._format_suite_name(base_name)

        self.out_cpp_path = os.path.join(out_dir, f"{self.out_base_name}.cpp")
        self.out_h_path = os.path.join(out_dir, f"{self.out_base_name}.h")

    def _format_suite_name(self, base_name):
        """Format test suite name according to configuration."""
        naming = self.config.naming
        camel = ''.join(word.capitalize() for word in base_name.split('_'))
        return f"{camel}{naming.suite_suffix}"

    def _format_test_name(self, func_name, path_index):
        """Format test case name according to configuration."""
        return self.config.naming.test_name_pattern.format(
            func=func_name, index=path_index)

    def _build_copyright_header(self):
        """Build copyright header lines if configured."""
        if not self.config.copyright_header:
            return []
        lines = []
        for line in self.config.copyright_header:
            lines.append(line)
        return lines

    def build_header(self):
        """Build the header file with function declarations."""
        guard = f"{self.out_base_name.upper()}_H"
        code = []
        # Add copyright header if configured
        code.extend(self._build_copyright_header())
        if self.config.copyright_header:
            code.append("")
        code.append(f"#ifndef {guard}")
        code.append(f"#define {guard}")
        code.append("")

        if self.project_includes:
            code.append("// --- Original Source Includes (Preserving Order) ---")
            for inc in self.project_includes:
                code.append(f"#include {inc}")
            code.append("")

        # Add user-specified extra includes
        if self.config.extra_includes:
            code.append("// --- User-Specified Extra Includes ---")
            for inc in self.config.extra_includes:
                code.append(f"#include {inc}")
            code.append("")

        all_globals = {}
        for func in self.funcs_info:
            for g_name, g_info in func.global_vars.items():
                all_globals[g_name] = g_info['type']

        code.append('extern "C" {')
        code.append("")

        if all_globals:
            code.append("// --- External Global Variables ---")
            for g_name, g_type in all_globals.items():
                # Convert C types to C++ compatible types (e.g., _Bool -> bool)
                g_type = self._c_to_cpp_type(g_type)
                # Fix function pointer declarations
                # Type string might be "int (*)(int, int)" or "int (*[4])(int, int)"
                # but we need "int (*global_math_op)(int, int)" or "int (*global_op_array[4])(int, int)"
                if '(*[' in g_type:
                    # Array of function pointers: "int (*[4])(int, int)" -> "int (*global_op_array[4])(int, int)"
                    fixed_type = g_type.replace('(*[', f'(*{g_name}[')
                    code.append(f"extern {fixed_type};")
                elif '(*)' in g_type:
                    # Simple function pointer: "int (*)(int, int)" -> "int (*global_math_op)(int, int)"
                    fixed_type = g_type.replace('(*)', f'(*{g_name})')
                    code.append(f"extern {fixed_type};")
                else:
                    code.append(f"extern {g_type} {g_name};")
            code.append("")

        code.append("// --- Target Function Declarations ---")
        for func in self.funcs_info:
            decl = func.get_declaration()
            # Convert C types to C++ compatible types
            decl = self._c_to_cpp_type(decl)
            code.append(decl)
        code.append("")

        if self.stub_builder:
            stub_decls = self.stub_builder.build_stub_declarations()
            if stub_decls:
                code.append("// --- Stub Function Declarations ---")
                for stub_decls in stub_decls:
                    stub_decl = self._c_to_cpp_type(stub_decls)
                    code.append(stub_decl)
                code.append("")

        code.append('} // extern "C"')
        code.append("")
        code.append(f"#endif // {guard}")
        return "\n".join(code)

    def _is_basic_type(self, canon_type_str):
        """Check if a type is considered a basic type."""
        t = canon_type_str.strip()
        # Use configurable basic type keywords
        basic_keywords = self.config.basic_type_keywords
        if '*' not in t and any(k in t for k in basic_keywords):
            return True
        return False

    def _c_to_cpp_type(self, type_str):
        """Convert C type keywords to C++ compatible types."""
        # Replace _Bool with bool for C++ compatibility
        result = type_str.replace('_Bool', 'bool')
        return result

    def build_cpp(self):
        """Build the C++ test file."""
        code = self._build_cpp_header()
        for func in self.funcs_info:
            for i, path in enumerate(func.paths, 1):
                code.extend(self._build_test_case(func, path, i))
        return "\n".join(code)

    def _build_cpp_header(self):
        """Build the header section of the C++ test file."""
        code = []
        # Add copyright header if configured
        code.extend(self._build_copyright_header())
        if self.config.copyright_header:
            code.append("")
        code.append("// --- Auto-generated GTest Framework ---")
        code.append("#include <gtest/gtest.h>")
        code.append(f'#include "{self.out_base_name}.h"')
        # Add user-specified extra includes
        if self.config.extra_includes:
            for inc in self.config.extra_includes:
                code.append(f"#include {inc}")
        code.append("")

        # Add stub macros if using stub framework
        if self.stub_framework:
            code.append("// --- Stub Macros ---")
            code.append("// Note: These macros provide basic stubbing support.")
            code.append("// For production use, more robust stubbing techniques may be needed.")
            code.append("#ifndef INSTALL_STUB")
            code.append("#define INSTALL_STUB(obj_func, stub_func) \\")
            code.append("    /* Function stubbing not fully supported - use link-time replacement */")
            code.append("#endif")
            code.append("")
            code.append("#ifndef UNINSTALL_STUB")
            code.append("#define UNINSTALL_STUB(obj_func) \\")
            code.append("    /* Function unstubbing not fully supported */")
            code.append("#endif")
            code.append("")
            code.append("#ifndef INSTALL_FUNC_PTR_STUB")
            code.append("#define INSTALL_FUNC_PTR_STUB(var, stub) \\")
            code.append("    do { \\")
            code.append("        static __typeof__(var) __saved_##var = var; \\")
            code.append("        var = stub; \\")
            code.append("    } while(0)")
            code.append("#endif")
            code.append("")
            code.append("#ifndef UNINSTALL_FUNC_PTR_STUB")
            code.append("#define UNINSTALL_FUNC_PTR_STUB(var) \\")
            code.append("    do { \\")
            code.append("        var = __saved_##var; \\")
            code.append("    } while(0)")
            code.append("#endif")
            code.append("")

        code.append(f"class {self.test_suite_name} : public ::testing::Test {{")
        code.append("protected:")
        code.append("    void SetUp() override {}")
        code.append("    void TearDown() override {}")
        code.append("};")
        code.append("")
        return code

    def _build_global_var_save(self, global_vars):
        """Generate code to save original values of global variables."""
        code = []
        if not global_vars:
            return code
        code.append("    // Save original global variable values")
        for g_name, g_info in global_vars.items():
            g_type = g_info['type']
            # Check if this is an array type (contains '[')
            is_array = '[' in g_type and ']' in g_type
            if is_array:
                # Arrays cannot be assigned - generate comment instead
                code.append(f"    // Note: Global array '{g_name}' cannot be saved/restored automatically")
            else:
                # Use __typeof__ for all types for simplicity and safety
                code.append(f"    __typeof__({g_name}) saved_{g_name} = {g_name};")
        code.append("")
        return code

    def _build_global_var_restore(self, global_vars):
        """Generate code to restore original values of global variables."""
        code = []
        if not global_vars:
            return code
        code.append("    // Restore original global variable values")
        for g_name, g_info in global_vars.items():
            g_type = g_info['type']
            # Check if this is an array type (contains '[')
            is_array = '[' in g_type and ']' in g_type
            if is_array:
                # Arrays cannot be assigned - skip restoration
                # (save code would have already skipped it)
                pass
            else:
                code.append(f"    {g_name} = saved_{g_name};")
        code.append("")
        return code

    def _build_test_case(self, func, path, path_index):
        """Build a single test case."""
        code = []
        code.append(f"// Note: Function '{func.name}' has a cyclomatic complexity of {func.complexity}, {len(func.paths)} test path(s) generated.")

        # Use configurable test name pattern
        test_name = self._format_test_name(func.name, path_index)
        desc = f"  // {path.description}" if path.description else ""
        code.append(f"TEST_F({self.test_suite_name}, {test_name}) {{{desc}")

        # Save global variables before any modifications
        if func.global_vars:
            code.extend(self._build_global_var_save(func.global_vars))

        # Install stubs before any setup
        if self.stub_framework and self.stub_builder and path.stub_constraints:
            for sc in path.stub_constraints:
                stub_name = self.stub_builder.stub_func_name(
                    sc.callee_name, func.name, path_index,
                    sc.is_function_pointer
                )
                if sc.is_function_pointer:
                    # Function pointer stub - skip local variables as they can't be stubbed from outside
                    if sc.pointer_source_type == "local":
                        # Local function pointer variables cannot be stubbed from outside the function
                        # The stub function for this constraint has not been generated
                        code.append(f"    // Note: Local function pointer variable '{sc.callee_name}' cannot be stubbed")
                        continue
                    var_name = sc.pointer_var_name or sc.callee_name
                    code.append(self.stub_framework.install_func_ptr_stub(
                        var_name, stub_name, sc.ret_type
                    ))
                else:
                    # Direct function stub
                    code.append(self.stub_framework.install_stub(
                        sc.callee_name, stub_name
                    ))
            code.append("")

        if self.construct and func.global_vars:
            code.extend(self._build_global_var_setup(func.global_vars, path.param_values))

        for param in func.params:
            code.extend(self._build_param_init(param, path.param_values, path_index))

        code.extend(self._build_func_call_and_assert(func, path, path_index))

        # Uninstall stubs after the call
        if self.stub_framework and path.stub_constraints:
            code.append("")
            for sc in path.stub_constraints:
                if sc.is_function_pointer:
                    # Function pointer stub - skip local variables as they can't be stubbed from outside
                    if sc.pointer_source_type == "local":
                        # Local function pointer variables cannot be stubbed from outside the function
                        continue
                    var_name = sc.pointer_var_name or sc.callee_name
                    code.append(self.stub_framework.uninstall_func_ptr_stub(var_name))
                else:
                    # Direct function stub
                    code.append(self.stub_framework.uninstall_stub(sc.callee_name))

        # Restore global variables after test
        if func.global_vars:
            code.extend(self._build_global_var_restore(func.global_vars))

        code.append("}")
        code.append("")
        return code

    def _build_field_access(self, base, field):
        """Build field access expression, handling array access syntax.

        Args:
            base: Base variable name (e.g., 'var_name' or 'var_name.field')
            field: Field name (e.g., 'field', '[index]', '[0]')
        Returns:
            Field access expression (e.g., 'var_name.field' or 'var_name[index]')
        """
        if field.startswith('['):
            return f"{base}{field}"
        else:
            return f"{base}.{field}"

    def _generate_field_assignments(self, var_name, val_dict, indent=4):
        """Generate field assignment code for nested dictionary values.

        Args:
            var_name: The base variable name (e.g., 'buffer' or 'buffer_val')
            val_dict: Dictionary mapping field names to values (scalar or nested dict)
            indent: Number of spaces for indentation
        Returns:
            List of code lines
        """
        code = []
        space = ' ' * indent
        for field, fval in val_dict.items():
            # Skip metadata fields (start and end with __)
            if field.startswith('__') and field.endswith('__'):
                continue

            if isinstance(fval, dict):
                # Check if this field is a pointer (has __ptr__ marker)
                is_ptr = fval.get('__ptr__', False)
                # Remove metadata fields
                clean_val_dict = {k: v for k, v in fval.items() if not (k.startswith('__') and k.endswith('__'))}

                # Check if this dict represents a scalar value stored under 'value' key
                # (e.g., leaf field with type information)
                if len(clean_val_dict) == 1 and 'value' in clean_val_dict and not isinstance(clean_val_dict['value'], dict):
                    # This is a scalar value with metadata (type, pointer flag)
                    scalar_value = clean_val_dict['value']
                    # Convert Python True/False to C true/false
                    if scalar_value is True:
                        scalar_str = "true"
                    elif scalar_value is False:
                        scalar_str = "false"
                    else:
                        scalar_str = str(scalar_value)
                    code.append(f"{space}{self._build_field_access(var_name, field)} = {scalar_str};")
                    continue  # Skip further processing

                # Check for nested 'value' dict (leaf field stored as {'value': {'value': actual_value}})
                if len(clean_val_dict) == 1 and 'value' in clean_val_dict and isinstance(clean_val_dict['value'], dict):
                    nested = clean_val_dict['value']
                    # Check if nested dict itself contains just a 'value' key with scalar
                    if len(nested) == 1 and 'value' in nested and not isinstance(nested['value'], dict):
                        scalar_value = nested['value']
                        if scalar_value is True:
                            scalar_str = "true"
                        elif scalar_value is False:
                            scalar_str = "false"
                        else:
                            scalar_str = str(scalar_value)
                        code.append(f"{space}{self._build_field_access(var_name, field)} = {scalar_str};")
                        continue  # Skip further processing

                if clean_val_dict:
                    if is_ptr:
                        # Pointer field: need to allocate memory for the pointed-to struct
                        # Generate a local variable for the pointed-to struct
                        ptr_var_name = f"{var_name}_{field}_val"
                        # Get type information if available
                        ptr_type = fval.get('__type__')
                        if ptr_type:
                            # Remove any '*' from the type since we're declaring the pointed-to type
                            # If ptr_type ends with '*', remove it
                            if ptr_type.endswith('*'):
                                pointed_type = ptr_type.rstrip('* ').strip()
                            else:
                                pointed_type = ptr_type
                            code.append(f"{space}// Allocate memory for pointer field '{field}'")
                            code.append(f"{space}{pointed_type} {ptr_var_name} = {{}};")
                        else:
                            # Type name is unknown, use a placeholder
                            code.append(f"{space}// TODO: Allocate memory for pointer field '{field}'")
                            code.append(f"{space}// Type unknown - replace 'UnknownType' with actual type")
                            code.append(f"{space}UnknownType {ptr_var_name} = {{}};")

                        # Special case: if clean_val_dict contains just a 'value' key that is a dict
                        # with a single 'value' key (scalar), treat it as a scalar field
                        if len(clean_val_dict) == 1 and 'value' in clean_val_dict and isinstance(clean_val_dict['value'], dict):
                            nested = clean_val_dict['value']
                            if len(nested) == 1 and 'value' in nested and not isinstance(nested['value'], dict):
                                scalar_value = nested['value']
                                if scalar_value is True:
                                    scalar_str = "true"
                                elif scalar_value is False:
                                    scalar_str = "false"
                                else:
                                    scalar_str = str(scalar_value)
                                code.append(f"{space}{ptr_var_name}.value = {scalar_str};")
                                # Assign pointer to point to the local variable
                                code.append(f"{space}{self._build_field_access(var_name, field)} = &{ptr_var_name};")
                                continue  # Skip the rest of pointer processing

                        # Generate assignments for fields of the pointed-to struct
                        for subfield, subval in clean_val_dict.items():
                            if isinstance(subval, dict):
                                # Nested struct under pointer
                                nested_code = self._generate_field_assignments(
                                    self._build_field_access(ptr_var_name, subfield), subval, indent
                                )
                                code.extend(nested_code)
                            else:
                                # Scalar field under pointer
                                if subval is True:
                                    subval_str = "true"
                                elif subval is False:
                                    subval_str = "false"
                                else:
                                    subval_str = str(subval)
                                code.append(f"{space}{self._build_field_access(ptr_var_name, subfield)} = {subval_str};")

                        # Assign pointer to point to the local variable
                        code.append(f"{space}{var_name}.{field} = &{ptr_var_name};")
                    else:
                        # Regular nested struct
                        nested_code = self._generate_field_assignments(
                            self._build_field_access(var_name, field), clean_val_dict, indent
                        )
                        code.extend(nested_code)
            else:
                # Scalar value assignment
                # Convert Python True/False to C true/false
                if fval is True:
                    fval_str = "true"
                elif fval is False:
                    fval_str = "false"
                else:
                    fval_str = str(fval)
                code.append(f"{space}{self._build_field_access(var_name, field)} = {fval_str};")
        return code

    def _build_global_var_setup(self, global_vars, param_values):
        """Build global variable setup code."""
        code = []
        for g_name, g_info in global_vars.items():
            val = param_values.get(g_name)
            g_type = g_info['type']
            canon_type = g_info['canonical_type']
            is_ptr = '*' in canon_type

            # Check if this is a function pointer type (heuristic: contains "(*)" or ")(*" or "(*[")
            is_func_ptr = ('(*)' in g_type) or (')(*' in g_type) or ('(*[' in g_type)
            # Check if this is an array type (contains '[')
            is_array = '[' in g_type and ']' in g_type

            if is_ptr and not is_func_ptr:
                base_type = g_type.replace('*', '').replace('const', '').strip()
                local = f"{g_name}_val"
                if isinstance(val, dict):
                    # Pointer with struct field constraints: allocate backing local, assign fields
                    code.append(f"    {base_type} {local} = {{}};")
                    # Generate field assignments (supports nested dictionaries)
                    field_assignments = self._generate_field_assignments(local, val)
                    code.extend(field_assignments)
                    code.append(f"    {g_name} = &{local};")
                elif val is not None:
                    # Scalar constraint on the pointer itself (e.g. NULL-check branch)
                    code.append(f"    {g_name} = {val};")
                else:
                    # No constraint: allocate a zero-initialized backing local to avoid NULL deref
                    code.append(f"    {base_type} {local} = {{}};")
                    code.append(f"    {g_name} = &{local};")
            else:
                # Handle array types specially - array names cannot be assigned
                if is_array:
                    if val is not None:
                        # Array with a constraint value - this is problematic
                        code.append(f"    // WARNING: Global array '{g_name}' has constraint '{val}' but array assignment is not supported")
                        code.append(f"    // TODO: Manually initialize array elements if needed")
                    else:
                        # No constraint - just add a comment
                        code.append(f"    // Global array '{g_name}' - initialize elements manually if needed")
                elif val is not None:
                    if isinstance(val, dict):
                        code.append(f"    {g_name} = {{}}; // Reset struct to avoid interference")
                        # Generate field assignments (supports nested dictionaries)
                        field_assignments = self._generate_field_assignments(g_name, val)
                        code.extend(field_assignments)
                    else:
                        code.append(f"    {g_name} = {val};")
                else:
                    def_val = self._default_value(canon_type)
                    code.append(f"    {g_name} = {def_val};")

        if global_vars:
            code.append("")
        return code

    def _format_param_type(self, param_type, param_name):
        """Format a parameter type with name, handling function pointers correctly."""
        # Handle function pointer types like "int (*)(int, int)" -> "int (*param_name)(int, int)"
        if '(*)' in param_type:
            # Simple function pointer: replace "(*)" with "(*param_name)"
            return param_type.replace('(*)', f'(*{param_name})')
        # Handle array of function pointers like "int (*[4])(int, int)" -> "int (*param_name[4])(int, int)"
        elif '(*[' in param_type:
            # Find the closing bracket after the opening [
            import re
            pattern = r'\(\*\[([^\]]+)\]\)'
            match = re.search(pattern, param_type)
            if match:
                array_size = match.group(1)
                # Replace "(*[4])" with "(*param_name[4])"
                return param_type.replace(f'(*[{array_size}])', f'(*{param_name}[{array_size}])')
        # Handle array types: convert "int[10] arr" to "int arr[10]"
        elif '[' in param_type and ']' in param_type:
            # Extract the array part
            type_parts = param_type.split('[')
            if len(type_parts) == 2:
                base_type = type_parts[0].strip()
                array_part = '[' + type_parts[1]
                return f"{base_type} {param_name}{array_part}"
        # Default: just type followed by name
        return f"{param_type} {param_name}"

    def _build_param_init(self, param, param_values, path_index):
        """Build parameter initialization code."""
        code = []
        ptype = self._c_to_cpp_type(param['type'])
        pname = param['name']
        canon_type = self._c_to_cpp_type(param['canonical_type'])

        if not self.construct:
            code.append(f"    {ptype} {pname} = /* init for path {path_index} */;")
            return code

        val = param_values.get(pname)
        is_ptr = '*' in ptype
        is_struct_like = isinstance(val, dict) and not self._is_basic_type(canon_type)

        # Check if this is a function pointer type (heuristic: contains "(*)" or ")(*" or "(*[")
        is_func_ptr = ('(*)' in ptype) or (')(*' in ptype) or ('(*[' in ptype)

        if is_struct_like:
            base_type = ptype.replace('*', '').replace('const', '').strip()
            if is_ptr:
                local = f"{pname}_val"
                code.append(f"    {base_type} {local} = {{}};")
                # Generate field assignments (supports nested dictionaries)
                field_assignments = self._generate_field_assignments(local, val)
                code.extend(field_assignments)
                code.append(f"    {ptype} {pname} = &{local};")
            else:
                code.append(f"    {ptype} {pname} = {{}};")
                # Generate field assignments (supports nested dictionaries)
                field_assignments = self._generate_field_assignments(pname, val)
                code.extend(field_assignments)
        elif is_ptr and val is None and not self._is_basic_type(canon_type) and not is_func_ptr:
            # Non-basic pointer with no constraint: allocate a backing local to avoid NULL deref
            # Skip for function pointers
            base_type = ptype.replace('*', '').replace('const', '').strip()
            local = f"{pname}_val"
            code.append(f"    {base_type} {local} = {{}};")
            code.append(f"    {ptype} {pname} = &{local};")
        else:
            scalar = val if (val is not None and not isinstance(val, dict)) else self._default_value(canon_type)
            if is_func_ptr:
                # Format function pointer type correctly: "int (*)(int, int)" -> "int (*pname)(int, int)"
                formatted = self._format_param_type(ptype, pname)
                code.append(f"    {formatted} = {scalar};")
            else:
                code.append(f"    {ptype} {pname} = {scalar};")
        return code

    def _build_func_call_and_assert(self, func, path, path_index):
        """Build function call and assertion code."""
        code = []
        args_str = [p['name'] for p in func.params]
        call_str = f"{func.name}({', '.join(args_str)});"

        if func.ret_type == "void":
            code.append(f"    {call_str}")
            return code

        # Format return type with variable name, handling function pointer types
        formatted_decl = self._format_type_and_name(func.ret_type, "result")
        code.append(f"    {formatted_decl} = {call_str}")

        if not self.construct or path.expected_return is None:
            code.append(f"    // EXPECT_EQ(result, /* expected for path {path_index} */);")
            return code

        ret_val = str(path.expected_return)
        if self._has_local_var_in_expr(ret_val):
            code.append(f"    // EXPECT_EQ(result, {ret_val}); // TODO: Cannot automatically resolve local variable '{ret_val}'")
        else:
            code.append(f"    EXPECT_EQ(result, {ret_val});")
        return code

    def _has_local_var_in_expr(self, expr):
        """Check if an expression contains local variable references."""
        words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expr)
        for w in words:
            if w in self.known_constants or w.isupper():
                continue
            if w not in ('true', 'false', 'nullptr', 'NULL'):
                return True
        return False

    def _format_type_and_name(self, type_str, name):
        """Format a type and variable name, handling function pointer types."""
        # Check if this is a function pointer type (contains "(*)" or ends with ")(*)")
        # For function pointer types like "int (*)(int, int)", we need to insert the name
        # to get "int (*name)(int, int)"
        import re

        # Pattern for function pointer types: return_type (*)(params)
        # Match patterns like "int (*)(int, int)" or "void (*)(void)"
        func_ptr_pattern = r'^([^(]+)\(\s*\*\s*\)\s*\(([^)]*)\)$'
        match = re.match(func_ptr_pattern, type_str.strip())
        if match:
            return_type = match.group(1).strip()
            params = match.group(2).strip()
            return f"{return_type} (*{name})({params})"

        # Another pattern: "int(*)(int,int)" without spaces
        func_ptr_pattern2 = r'^([^(]+)\(\*\)\(([^)]*)\)$'
        match = re.match(func_ptr_pattern2, type_str.strip())
        if match:
            return_type = match.group(1).strip()
            params = match.group(2).strip()
            return f"{return_type} (*{name})({params})"

        # Not a function pointer type, use normal formatting
        return f"{type_str} {name}"

    def _default_value(self, canon_type_str):
        """Get default value for a type using configuration."""
        cfg = self.config.default_values
        t = canon_type_str.strip()

        # First check custom type defaults
        for custom_type, default in cfg.custom_type_defaults.items():
            if custom_type in t:
                return default

        # Check pointer type
        if '*' in t:
            return cfg.pointer_default

        # Check floating point types
        if any(k in t for k in ('float', 'double')):
            return cfg.float_default

        # Check integer/bool types
        if any(k in t for k in ('int', 'uint', 'char', 'long', 'short', 'bool', 'size_t', 'unsigned', 'signed')):
            return cfg.int_default

        # Default to struct/empty initializer
        return cfg.struct_default