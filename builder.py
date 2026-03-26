"""GTest builder with configurable naming and default values."""

import os
import re

from models import PathConstraint, FunctionInfo
from config import GeneratorConfig


class GTestBuilder:
    """Responsible for generating GTest framework code with configurable naming and defaults."""

    def __init__(self, source_file, funcs_info, known_constants,
                 config: GeneratorConfig, outdir=None, project_includes=None, construct=False):
        self.source_file = source_file
        self.funcs_info = funcs_info
        self.known_constants = known_constants
        self.project_includes = project_includes or []
        self.construct = construct
        self.config = config

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

    def build_header(self):
        """Build the header file with function declarations."""
        guard = f"{self.out_base_name.upper()}_H"
        code = []
        code.append(f"#ifndef {guard}")
        code.append(f"#define {guard}")
        code.append("")

        if self.project_includes:
            code.append("// --- Original Source Includes (Preserving Order) ---")
            for inc in self.project_includes:
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
                code.append(f"extern {g_type} {g_name};")
            code.append("")

        code.append("// --- Target Function Declarations ---")
        for func in self.funcs_info:
            code.append(func.get_declaration())
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
        code.append("// --- Auto-generated GTest Framework ---")
        code.append("#include <gtest/gtest.h>")
        code.append(f'#include "{self.out_base_name}.h"')
        code.append("")
        code.append(f"class {self.test_suite_name} : public ::testing::Test {{")
        code.append("protected:")
        code.append("    void SetUp() override {}")
        code.append("    void TearDown() override {}")
        code.append("};")
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

        if self.construct and func.global_vars:
            code.extend(self._build_global_var_setup(func.global_vars, path.param_values))

        for param in func.params:
            code.extend(self._build_param_init(param, path.param_values, path_index))

        code.extend(self._build_func_call_and_assert(func, path, path_index))
        code.append("}")
        code.append("")
        return code

    def _build_global_var_setup(self, global_vars, param_values):
        """Build global variable setup code."""
        code = []
        for g_name, g_info in global_vars.items():
            val = param_values.get(g_name)
            canon_type = g_info['canonical_type']

            if val is not None:
                if isinstance(val, dict):
                    code.append(f"    {g_name} = {{}}; // Reset struct to avoid interference")
                    for field, fval in val.items():
                        code.append(f"    {g_name}.{field} = {fval};")
                else:
                    code.append(f"    {g_name} = {val};")
            else:
                def_val = self._default_value(canon_type)
                code.append(f"    {g_name} = {def_val};")

        if global_vars:
            code.append("")
        return code

    def _build_param_init(self, param, param_values, path_index):
        """Build parameter initialization code."""
        code = []
        ptype = param['type']
        pname = param['name']
        canon_type = param['canonical_type']

        if not self.construct:
            code.append(f"    {ptype} {pname} = /* init for path {path_index} */;")
            return code

        val = param_values.get(pname)
        is_ptr = '*' in ptype
        is_struct_like = isinstance(val, dict) and not self._is_basic_type(canon_type)

        if is_struct_like:
            base_type = ptype.replace('*', '').replace('const', '').strip()
            if is_ptr:
                local = f"{pname}_val"
                code.append(f"    {base_type} {local} = {{}};")
                for field, fval in val.items():
                    code.append(f"    {local}.{field} = {fval};")
                code.append(f"    {ptype} {pname} = &{local};")
            else:
                code.append(f"    {ptype} {pname} = {{}};")
                for field, fval in val.items():
                    code.append(f"    {pname}.{field} = {fval};")
        else:
            scalar = val if (val is not None and not isinstance(val, dict)) else self._default_value(canon_type)
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

        code.append(f"    {func.ret_type} result = {call_str}")

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