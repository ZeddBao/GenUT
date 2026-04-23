"""GTest builder with configurable naming and default values."""

import os
import re

from .models import PathConstraint, FunctionInfo
from .config import GeneratorConfig


class GTestBuilder:
    """Responsible for generating GTest framework code with configurable naming and defaults."""

    # Compiled once at class level — used by _has_local_var_in_expr and _condition_has_unconstrained_local
    _STRIP_LITERALS_PAT = re.compile(
        r'(?<![A-Za-z_0-9])-?(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)[fFlLuU]*'
    )
    # C++ keywords that are valid in generated code and must not be flagged as "local variables"
    _CPP_KEYWORDS = frozenset({'true', 'false', 'nullptr', 'NULL', 'void'})

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
        # Function pointer helpers: func_ptr_type_str → (helper_name, ret_type, param_types)
        self._func_ptr_helpers = {}
        self._func_ptr_helper_counter = 0

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

        # Add user-specified extra includes (C++ headers, placed before extern "C")
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

        # Place original C source includes inside extern "C" to avoid linkage conflicts
        if self.project_includes:
            code.append("// --- Original Source Includes (Preserving Order) ---")
            for inc in self.project_includes:
                code.append(f"#include {inc}")
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
                    # If type ends with *, don't add space between type and name
                    g_type_stripped = g_type.rstrip()
                    if g_type_stripped.endswith('*'):
                        code.append(f"extern {g_type_stripped}{g_name};")
                    else:
                        code.append(f"extern {g_type_stripped} {g_name};")
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

    @property
    def _basic_type_pattern(self):
        """Compiled regex for basic type keywords — cached on first access."""
        if not hasattr(self, '_basic_type_pattern_cache'):
            kws = self.config.basic_type_keywords
            self._basic_type_pattern_cache = re.compile(
                '|'.join(rf'\b{re.escape(k)}\b' for k in kws)
            )
        return self._basic_type_pattern_cache

    def _is_basic_type(self, canon_type_str):
        """Check if a type is considered a basic type."""
        t = canon_type_str.strip()
        return '*' not in t and bool(self._basic_type_pattern.search(t))

    def _c_to_cpp_type(self, type_str):
        """Convert C type keywords to C++ compatible types."""
        # Replace _Bool with bool for C++ compatibility
        result = type_str.replace('_Bool', 'bool')
        return result

    def build_cpp(self):
        """Build the C++ test file."""
        # First pass: generate test cases (this populates self._func_ptr_helpers)
        test_cases = []
        for func in self.funcs_info:
            test_cases.append(f"// Function '{func.name}': cyclomatic complexity = {func.complexity}, test paths generated = {len(func.paths)}")
            for i, path in enumerate(func.paths, 1):
                test_cases.extend(self._build_test_case(func, path, i))

        # Second pass: assemble output — helpers (if any) go before test cases
        code = self._build_cpp_header()
        if self._func_ptr_helpers:
            if self.stub_builder is not None:
                # Definitions are in _stub.cpp; only emit forward declarations here
                code.append("// --- Function Pointer Stub Declarations (defined in _stub.cpp) ---")
                for _, (helper_name, ret_type, param_types) in self._func_ptr_helpers.items():
                    params_str = ", ".join(f"{pt} arg{i}" for i, pt in enumerate(param_types)) if param_types else "void"
                    ret_stripped = ret_type.rstrip()
                    sep = "" if ret_stripped.endswith("*") else " "
                    code.append(f"{ret_stripped}{sep}{helper_name}({params_str});")
            else:
                # No stub file — keep static definitions inline
                code.append("// --- Function Pointer Stubs for non-NULL paths ---")
                for _, (helper_name, ret_type, param_types) in self._func_ptr_helpers.items():
                    code.append(self._make_fp_helper_defn(helper_name, ret_type, param_types, static=True))
            code.append("")
        code.extend(test_cases)
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
                g_type_cpp = self._c_to_cpp_type(g_type)
                formatted = self._format_param_type(g_type_cpp, f"saved_{g_name}")
                code.append(f"    {formatted} = {g_name};")
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

        # Declare scalar/basic params before struct params so array-subscript
        # references (e.g. items[index]) are already in scope when struct fields are set.
        param_order = {p['name']: i for i, p in enumerate(func.params)}
        def _is_struct_param(p):
            val = path.param_values.get(p['name'])
            canon = self._c_to_cpp_type(p['canonical_type'])
            return isinstance(val, dict) and not self._is_basic_type(canon)
        ordered_params = sorted(func.params, key=lambda p: (1 if _is_struct_param(p) else 0, param_order[p['name']]))
        for param in ordered_params:
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
                    scalar_str = self._clean_scalar_value(clean_val_dict['value'])
                    if scalar_str == "(void*)1":
                        type_str = fval.get('__type__', "")
                        is_fptr = '(*)' in type_str or ')(*' in type_str
                        if is_fptr:
                            scalar_str = self._get_or_create_fp_helper(type_str)
                        else:
                            # (void*)1 is always a non-NULL placeholder from the extractor;
                            # construct a backing local variable for the pointed-to type
                            base_type = type_str.replace('*', '').replace('const', '').strip() if type_str else None
                            local = f"{var_name}_{field}_ptr_val"
                            if base_type:
                                code.append(f"{space}{base_type} {local} = {{}};")
                                code.append(f"{space}{self._build_field_access(var_name, field)} = &{local};")
                            else:
                                code.append(f"{space}// TODO: {field} needs a non-NULL pointer; assign manually")
                                code.append(f"{space}{self._build_field_access(var_name, field)} = NULL;")
                            continue
                    code.append(f"{space}{self._build_field_access(var_name, field)} = {scalar_str};")
                    continue  # Skip further processing

                # Check for nested 'value' dict (leaf field stored as {'value': {'value': actual_value}})
                if len(clean_val_dict) == 1 and 'value' in clean_val_dict and isinstance(clean_val_dict['value'], dict):
                    nested = clean_val_dict['value']
                    # Check if nested dict itself contains just a 'value' key with scalar
                    if len(nested) == 1 and 'value' in nested and not isinstance(nested['value'], dict):
                        scalar_str = self._clean_scalar_value(nested['value'])
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

                        # Generate assignments for fields of the pointed-to struct.
                        # Skip 'value' string entries — they represent the pointer's own
                        # NULL/(void*)1 sentinel, not a field of the pointed-to struct.
                        for subfield, subval in clean_val_dict.items():
                            if subfield == 'value' and not isinstance(subval, dict):
                                continue  # pointer-value sentinel, not a struct field
                            if isinstance(subval, dict):
                                # Check if this is a scalar leaf: {value: X, __type__: Y}
                                clean_subval = {k: v for k, v in subval.items()
                                                if not (k.startswith('__') and k.endswith('__'))}
                                if (len(clean_subval) == 1 and 'value' in clean_subval
                                        and not isinstance(clean_subval['value'], dict)):
                                    scalar_str = self._clean_scalar_value(clean_subval['value'])
                                    code.append(f"{space}{self._build_field_access(ptr_var_name, subfield)} = {scalar_str};")
                                else:
                                    # Nested struct under pointer
                                    nested_code = self._generate_field_assignments(
                                        self._build_field_access(ptr_var_name, subfield), subval, indent
                                    )
                                    code.extend(nested_code)
                            else:
                                # Scalar field under pointer
                                subval_str = self._clean_scalar_value(subval)
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
                fval_str = self._clean_scalar_value(fval)
                code.append(f"{space}{self._build_field_access(var_name, field)} = {fval_str};")
        return code

    @staticmethod
    def _backing_type(base_type):
        """Return 'char' in place of 'void' (void locals are illegal in C/C++)."""
        return "char" if base_type == "void" else base_type

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
                backing = self._backing_type(base_type)
                local = f"{g_name}_val"
                if isinstance(val, dict):
                    # Pointer with struct field constraints: allocate backing local, assign fields
                    code.append(f"    {backing} {local} = {{}};")
                    field_assignments = self._generate_field_assignments(local, val)
                    code.extend(field_assignments)
                    code.append(f"    {g_name} = &{local};")
                elif val is not None:
                    scalar = self._clean_scalar_value(val)
                    if scalar == "(void*)1" and "char" in canon_type:
                        scalar = '""'
                    code.append(f"    {g_name} = {scalar};")
                else:
                    # No constraint: allocate a zero-initialized backing local to avoid NULL deref
                    code.append(f"    {backing} {local} = {{}};")
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
                        field_assignments = self._generate_field_assignments(g_name, val)
                        code.extend(field_assignments)
                    else:
                        scalar = self._clean_scalar_value(val)
                        if scalar == "(void*)1":
                            if is_func_ptr:
                                scalar = self._get_or_create_fp_helper(g_type)
                            elif "char" in canon_type:
                                scalar = '""'
                        code.append(f"    {g_name} = {scalar};")
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
        # If type ends with *, don't add space between type and name
        param_type_stripped = param_type.rstrip()
        if param_type_stripped.endswith('*'):
            return f"{param_type_stripped}{param_name}"
        return f"{param_type_stripped} {param_name}"

    def _get_alternative_value(self, canon_type_str, avoid_values=None):
        """Get an alternative scalar value, avoiding conflict with other path values.

        When a constraint resolution fails (e.g., unresolvable macro), use this to generate
        a fallback value that doesn't match values used in other paths for the same parameter.
        """
        if avoid_values is None:
            avoid_values = set()

        default_val = self._default_value(canon_type_str)

        # For numeric types, try to find an alternative if default conflicts
        if re.match(r'^-?\d+$', str(default_val)):
            try:
                current = int(default_val)
                # Try a few alternatives: current+1, current-1, current+2, etc.
                for offset in [1, -1, 2, -2, 3, -3]:
                    alternative = current + offset
                    if str(alternative) not in avoid_values and alternative >= 0:
                        return str(alternative)
            except (ValueError, TypeError):
                pass

        return default_val

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

        # Handle array types (e.g., "int [10]") — must be formatted as "int arr[10]"
        is_array_type = ('[' in ptype and ']' in ptype
                         and '(*)' not in ptype and '(*[' not in ptype)
        if is_array_type:
            formatted = self._format_param_type(ptype, pname)
            code.append(f"    {formatted} = {{}};")
            if isinstance(val, dict):
                field_assignments = self._generate_field_assignments(pname, val)
                code.extend(field_assignments)
            return code

        if is_struct_like:
            base_type = ptype.replace('*', '').replace('const', '').strip()
            if is_ptr:
                local = f"{pname}_val"
                if base_type == "char":
                    max_idx = -1
                    if isinstance(val, dict):
                        for k in val.keys():
                            if not (k.startswith('__') and k.endswith('__')):
                                m2 = re.match(r'^\[(\d+)\]$', str(k))
                                if m2:
                                    max_idx = max(max_idx, int(m2.group(1)))
                    arr_size = max(max_idx + 2, 8)
                    code.append(f"    {base_type} {local}[{arr_size}] = {{}};")
                    field_assignments = self._generate_field_assignments(local, val)
                    code.extend(field_assignments)
                    # char arrays decay to char* — use without &
                    code.append(f"    {ptype} {pname} = {local};")
                else:
                    backing = self._backing_type(base_type)
                    code.append(f"    {backing} {local} = {{}};")
                    field_assignments = self._generate_field_assignments(local, val)
                    code.extend(field_assignments)
                    code.append(f"    {ptype} {pname} = &{local};")
            else:
                code.append(f"    {ptype} {pname} = {{}};")
                field_assignments = self._generate_field_assignments(pname, val)
                code.extend(field_assignments)
        elif is_ptr and val is None and not self._is_basic_type(canon_type) and not is_func_ptr:
            # Non-basic pointer with no constraint: allocate a backing local to avoid NULL deref
            base_type = ptype.replace('*', '').replace('const', '').strip()
            local = f"{pname}_val"
            backing = self._backing_type(base_type)
            code.append(f"    {backing} {local} = {{}};")
            code.append(f"    {ptype} {pname} = &{local};")
        else:
            scalar = val if (val is not None and not isinstance(val, dict)) else self._default_value(canon_type)
            scalar = self._clean_scalar_value(scalar)
            # If the scalar is a /* TODO: */ placeholder (unresolvable negation) or references
            # a function-internal local variable, fall back to the type default so the code compiles.
            if scalar.startswith("/* TODO:") or self._has_local_var_in_expr(scalar):
                # Collect values used by other paths to avoid collision
                avoid_values = set()
                func = self.funcs_info[0]  # Assuming current function is first
                for path in func.paths:
                    path_val = path.param_values.get(pname)
                    if path_val is not None and not isinstance(path_val, dict):
                        avoid_values.add(str(path_val))
                scalar = self._get_alternative_value(canon_type, avoid_values)
            # Treat small positive integers as non-NULL placeholders for pointer types
            # (the bare boolean check in the extractor returns 1 for != 0 on pointer params)
            if is_ptr and not is_func_ptr and re.match(r'^\d+$', scalar) and scalar not in ('0',):
                scalar = "(void*)1"
            # (void*)1 is a non-NULL placeholder — construct a real stack variable instead
            if scalar == "(void*)1":
                if is_func_ptr:
                    scalar = self._get_or_create_fp_helper(ptype)
                else:
                    base_type = ptype.replace('*', '').replace('const', '').strip()
                    local = f"{pname}_val"
                    if "char" in base_type:
                        code.append(f"    {base_type} {local}[] = \"\";")
                        code.append(f"    {ptype} {pname} = {local};")
                    else:
                        backing = self._backing_type(base_type)
                        code.append(f"    {backing} {local} = {{}};")
                        code.append(f"    {ptype} {pname} = &{local};")
                    return code
            if is_func_ptr:
                # Format function pointer type correctly: "int (*)(int, int)" -> "int (*pname)(int, int)"
                formatted = self._format_param_type(ptype, pname)
                code.append(f"    {formatted} = {scalar};")
            else:
                # For non-basic types (e.g., enums), a numeric initializer needs an explicit cast
                if (not is_ptr and re.match(r'^-?\d+$', str(scalar))
                        and not self._is_basic_type(canon_type)):
                    scalar = f"({ptype}){scalar}"
                code.append(f"    {ptype} {pname} = {scalar};")
        return code

    def _build_func_call_and_assert(self, func, path, path_index):
        """Build function call and assertion code."""
        code = []
        args_str = [p['name'] for p in func.params]
        call_str = f"{func.name}({', '.join(args_str)});"

        if func.ret_type == "void":
            code.append(f"    {call_str}")
            if self.construct:
                # Placeholder assertions for observable side effects of void functions.
                # 1. Writable (non-const) pointer params that are non-NULL in this path.
                for p in func.params:
                    pname = p['name']
                    ptype = p['type']
                    if '*' not in ptype or 'const' in ptype:
                        continue
                    val = path.param_values.get(pname)
                    is_null = (val == 'NULL' or str(val) == 'NULL')
                    if not is_null:
                        code.append(f"    // EXPECT_EQ(*{pname}, /* expected */);")
                # 2. Global variables modified in this function.
                for g_name in func.global_vars:
                    code.append(f"    // EXPECT_EQ({g_name}, /* expected */);")
            return code

        # Format return type with variable name, handling function pointer types
        formatted_decl = self._format_type_and_name(self._c_to_cpp_type(func.ret_type), "result")
        code.append(f"    {formatted_decl} = {call_str}")

        if not self.construct or path.expected_return is None:
            code.append(f"    // EXPECT_EQ(result, /* expected for path {path_index} */);")
            return code

        ret_val = str(path.expected_return)
        # GTest EXPECT_EQ can't compare pointer types with NULL (int 0); use nullptr instead
        if ret_val == "NULL" and '*' in func.ret_type:
            ret_val = "nullptr"
        if self._has_local_var_in_expr(ret_val):
            code.append(f"    // EXPECT_EQ(result, {ret_val}); // TODO: Cannot automatically resolve local variable '{ret_val}'")
        elif self._condition_has_unconstrained_local(path, func) and not path.stub_constraints:
            # Path condition references a local C variable that isn't a param/global,
            # and no stub is installed to control it — inputs may not reach this branch.
            code.append(f"    // EXPECT_EQ(result, {ret_val}); // NOTE: path condition involves a local variable; inputs may not trigger this branch")
        elif self._condition_has_compound_operator(path, func):
            # Path condition involves compound bitwise or division expressions (e.g. a & b, a / b).
            # Constraint extraction for these is unreliable; inputs may not trigger this branch.
            code.append(f"    // EXPECT_EQ(result, {ret_val}); // NOTE: compound bitwise/arithmetic condition; inputs may not trigger this branch")
        else:
            code.append(f"    EXPECT_EQ(result, {ret_val});")
        return code

    def _condition_has_unconstrained_local(self, path, func):
        """Check if the path's condition description references local C variables (not params/globals).

        When a branch condition is on a local variable (e.g., `result > 1e38f` where `result`
        is computed inside the function), the generated test inputs may not actually reach that
        branch. In such cases, the EXPECT_EQ assertion could give a false failure.
        """
        param_names = {p['name'] for p in func.params}
        global_names = set(func.global_vars.keys())
        op_keywords = {'else', 'implicit', 'default'}
        allowed = param_names | global_names | self.known_constants | op_keywords

        desc = path.description or ""
        if desc and self._has_local_var_in_expr(desc, allowed=allowed):
            return True
        # For 'else' / 'else (implicit)' paths, also check the immediately preceding
        # non-else sibling — if that sibling's condition references a local variable,
        # this else branch also can't be reliably reached with the generated inputs.
        if desc in ("else", "else (implicit)") and func.paths:
            idx = func.paths.index(path)
            for j in range(idx - 1, -1, -1):
                prev_desc = func.paths[j].description or ""
                if prev_desc not in ("else", "else (implicit)"):
                    if self._has_local_var_in_expr(prev_desc, allowed=allowed):
                        return True
                    # For multi-variable compound equality conditions like
                    # "a == X && b == Y && c == Z" (row-matching patterns in orthogonal
                    # arrays), the negated inputs for the else path may go out-of-range
                    # and trigger an earlier validity check, making EXPECT_EQ unreliable.
                    eq_matches = re.findall(r'\b\w+\s*==\s*\w+', prev_desc)
                    if len(eq_matches) > 1 and '&&' in prev_desc:
                        return True
                    break
        return False

    def _condition_has_compound_operator(self, path, func):
        """Check if this path (or any path in the same function chain) has a condition
        involving compound bitwise or division expressions that the extractor can't reliably solve.

        Detects conditions like '( flags & mask ) != 0', 'a / b > 10', or else-paths that
        follow such conditions in an if-else chain.
        """
        # Check the path's own description for compound operators
        if self._desc_has_compound_operator(path.description or ""):
            return True
        # For 'else' / 'else (implicit)' / 'default' paths, check if any sibling path
        # in the same function has a compound-operator condition. If so, the else branch
        # inherits accumulated wrong constraints from those negations.
        desc = path.description or ""
        if desc in ("else", "else (implicit)", "default") and func.paths:
            for sibling in func.paths:
                if sibling is path:
                    continue
                if self._desc_has_compound_operator(sibling.description or ""):
                    return True
        return False

    @staticmethod
    def _desc_has_compound_operator(desc):
        """Return True if a path description contains compound operators that the constraint
        extractor cannot reliably solve for individual variables.

        This includes:
        - Compound bitwise: a & b, a | b, a ^ b (not logical && / ||)
        - Compound arithmetic in condition: a / b, a * b, a + b, a - b, a % b  OP  literal
          (where the operands include at least two variables or a variable-arithmetic-variable expression)
        - Complex negation: !(compound_expr)
        """
        if not desc:
            return False
        # Bitwise AND: ' & ' but not '&&'
        if re.search(r'(?<![&])\s&\s(?![&])', desc):
            return True
        # Bitwise OR: ' | ' but not '||'
        if re.search(r'(?<![|])\s\|\s(?![|])', desc):
            return True
        # Bitwise XOR: '^'
        if '^' in desc:
            return True
        # Compound arithmetic in condition: two identifiers joined by +/-/*//%/ with comparison
        # e.g. 'a + b > 100', 'a - b < 0', 'a * b == 0', 'a / b > 10', 'a % b == 0'
        if re.search(r'\b\w+\s*[+\-*/%]\s*\w+\s*(?:>|>=|<|<=|==|!=)', desc):
            return True
        # Bitwise NOT / complex logical NOT over compound expr: '! ( expr )' where expr has operators
        if re.search(r'!\s*\([^)]*\b\w+\s*(?:==|!=|>|<|>=|<=|&&|\|\|)\s*\w+[^)]*\)', desc):
            return True
        return False

    def _has_local_var_in_expr(self, expr, allowed=None):
        """Check if an expression contains local variable references.

        When `allowed` is provided, any identifier in that set is treated as known.
        When omitted, known_constants + all-caps identifiers + C++ keywords are allowed.
        """
        clean = self._STRIP_LITERALS_PAT.sub('', expr)
        words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', clean)
        if allowed is not None:
            return bool(set(words) - allowed - self._CPP_KEYWORDS)
        return any(
            w not in self.known_constants and not w.isupper() and w not in self._CPP_KEYWORDS
            for w in words
        )

    def _format_type_and_name(self, type_str, name):
        """Format a type and variable name, handling function pointer types."""
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
        # If type ends with *, don't add space between type and name
        type_str_stripped = type_str.rstrip()
        if type_str_stripped.endswith('*'):
            return f"{type_str_stripped}{name}"
        return f"{type_str_stripped} {name}"

    def _parse_func_ptr_type(self, func_ptr_type):
        """Parse 'int (*)(int, int)' → (ret_type, [param_type_str, ...]).
        Returns (None, None) on failure.
        """
        t = func_ptr_type.strip()
        m = re.match(r'^(.*?)\(\s*\*\s*\)\s*\((.*)\)$', t, re.DOTALL)
        if not m:
            return None, None
        ret_type = m.group(1).strip()
        params_str = m.group(2).strip()
        if not params_str or params_str == 'void':
            return ret_type, []
        return ret_type, [p.strip() for p in params_str.split(',')]

    def _make_fp_helper_defn(self, helper_name, ret_type, param_types, static=True):
        """Return a C++ function definition for use as a non-NULL function pointer value."""
        if param_types:
            params = [f"{pt} arg{i}" for i, pt in enumerate(param_types)]
            params_str = ", ".join(params)
            void_stmts = " ".join(f"(void)arg{i};" for i in range(len(param_types)))
        else:
            params_str = "void"
            void_stmts = ""
        if ret_type == "void":
            body = f"{{ {void_stmts} }}" if void_stmts else "{ }"
        else:
            default_ret = self._default_value(ret_type)
            body = f"{{ {void_stmts} return {default_ret}; }}" if void_stmts else f"{{ return {default_ret}; }}"
        prefix = "static " if static else ""
        return f"{prefix}{ret_type} {helper_name}({params_str}) {body}"

    def _get_or_create_fp_helper(self, func_ptr_type):
        """Return the name of a static helper function for the given function pointer type,
        creating it on first use. Falls back to NULL if the type cannot be parsed.
        """
        if func_ptr_type in self._func_ptr_helpers:
            return self._func_ptr_helpers[func_ptr_type][0]
        ret_type, param_types = self._parse_func_ptr_type(func_ptr_type)
        if ret_type is None:
            return "NULL"
        helper_name = f"_fp_stub_{self._func_ptr_helper_counter}"
        self._func_ptr_helper_counter += 1
        self._func_ptr_helpers[func_ptr_type] = (helper_name, ret_type, param_types)
        if self.stub_builder is not None:
            self.stub_builder.add_fp_helper(helper_name, ret_type, param_types)
        return helper_name

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

    def _clean_scalar_value(self, value):
        """Convert a scalar value to a valid C++ expression string.

        Handles Python booleans (True/False → "true"/"false") and comment-form
        placeholder strings like "/* not SOME_CONST */" produced by the constraint
        extractor for unresolvable negated literals.
        """
        if value is True:
            return "true"
        if value is False:
            return "false"
        if not isinstance(value, str):
            return str(value)
        value_str = value.strip()
        if value_str.startswith("/*") and value_str.endswith("*/"):
            inner = value_str[2:-2].strip()
            if inner.startswith("not "):
                return f"/* TODO: {inner} */"
            return f"/* TODO: unrecognized comment value: {inner} */"
        return value_str