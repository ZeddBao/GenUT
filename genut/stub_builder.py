"""Stub code generator: produces stub declarations and implementations."""

import os


class StubBuilder:
    """Generates stub function declarations (for .h) and implementations (_stub.cpp)."""

    def __init__(self, source_file, funcs_info, config, outdir=None):
        self.funcs_info = funcs_info
        self.config = config
        out_dir = os.path.abspath(outdir) if outdir else os.path.dirname(os.path.abspath(source_file))
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        naming = config.naming
        out_base = f"{naming.file_prefix}{base_name}{naming.file_suffix}"
        self.out_base_name = out_base
        self.out_stub_cpp_path = os.path.join(out_dir, f"{out_base}_stub.cpp")

    def _build_copyright_header(self):
        """Build copyright header lines if configured."""
        if not self.config.copyright_header:
            return []
        lines = []
        for line in self.config.copyright_header:
            lines.append(line)
        return lines

    def _iter_stubs(self):
        """Yield (func, path_index, stub_constraint) for all paths that need stubs."""
        for func in self.funcs_info:
            for i, path in enumerate(func.paths, 1):
                for sc in path.stub_constraints:
                    # Skip stub constraints for local function pointer variables
                    # as they cannot be stubbed from outside the function
                    if sc.is_function_pointer and sc.pointer_source_type == "local":
                        continue
                    yield func, i, sc

    def stub_func_name(self, callee_name, func_name, path_index, is_function_pointer=False):
        """Canonical stub function name."""
        if is_function_pointer:
            return f"stub_ptr_{callee_name}_{func_name}_{path_index}"
        else:
            return f"stub_{callee_name}_{func_name}_{path_index}"

    def build_stub_declarations(self):
        """Return a list of declaration strings to embed in the .h file."""
        seen = set()
        decls = []
        for func, i, sc in self._iter_stubs():
            name = self.stub_func_name(sc.callee_name, func.name, i, sc.is_function_pointer)
            if name in seen:
                continue
            seen.add(name)
            if sc.params:
                param_str = ", ".join(self._format_param_type(p['type'], p['name']) for p in sc.params)
            else:
                param_str = "void"
            # Use _format_function_declaration for correct function pointer return type formatting
            decls.append(f"{self._format_function_declaration(sc.ret_type, name, param_str)};")
        return decls

    def _is_function_pointer_type(self, type_str):
        """Check if a type string represents a function pointer."""
        # Simple heuristic: function pointer types contain "(*)"
        return "(*)" in type_str

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

    def _format_function_declaration(self, ret_type, func_name, param_str):
        """Format a function declaration, handling function pointer return types."""
        # Check if return type is a function pointer (contains "(*)" )
        if "(*)" in ret_type:
            # Function returning a function pointer: format as "int (*func_name(params))(func_params)"
            # Replace "(*)" with "(*{func_name}({param_str}))"
            return ret_type.replace("(*)", f"(*{func_name}({param_str}))")
        else:
            # Normal function declaration
            return f"{ret_type} {func_name}({param_str})"

    def build_stub_cpp(self):
        """Generate the full content of the _stub.cpp file."""
        lines = []
        # Add copyright header if configured
        lines.extend(self._build_copyright_header())
        if self.config.copyright_header:
            lines.append("")
        lines.append("// --- Auto-generated Stub Implementations ---")
        lines.append(f'#include "{self.out_base_name}.h"')
        # Add user-specified extra includes
        if self.config.extra_includes:
            for inc in self.config.extra_includes:
                lines.append(f"#include {inc}")
        lines.append("")

        seen = set()
        for func, i, sc in self._iter_stubs():
            name = self.stub_func_name(sc.callee_name, func.name, i, sc.is_function_pointer)
            if name in seen:
                continue
            seen.add(name)

            # Comment block
            path = func.paths[i - 1]
            lines.append(f"// Stub for: {sc.callee_name}")
            lines.append(f"// Used in: {func.name}_Path{i}"
                         + (f"  // {path.description}" if path.description else ""))

            # Function signature
            if sc.params:
                param_str = ", ".join(self._format_param_type(p['type'], p['name']) for p in sc.params)
            else:
                param_str = "void"
            # Use _format_function_declaration for correct function pointer return type formatting
            lines.append(f"{self._format_function_declaration(sc.ret_type, name, param_str)} {{")

            # Suppress unused parameter warnings
            for p in sc.params:
                lines.append(f"    (void){p['name']};")

            # Handle output parameters
            for arg_index, (var_name, value) in sc.output_params.items():
                if arg_index < len(sc.params):
                    param = sc.params[arg_index]
                    param_name = param['name']
                    param_type = param['type']
                    # Simple heuristic: if param_type ends with * it's a pointer
                    if param_type.strip().endswith('*'):
                        lines.append(f"    *{param_name} = {value};")
                    else:
                        lines.append(f"    // TODO: set output parameter {param_name} (type {param_type}) to {value}")
                else:
                    lines.append(f"    // ERROR: arg_index {arg_index} out of range for {sc.callee_name}")

            # Return value
            if sc.ret_type != 'void' and sc.return_value:
                # Clean up comment-like return values (e.g., "/* not NULL */")
                return_value = sc.return_value.strip()
                if return_value.startswith("/*") and return_value.endswith("*/"):
                    # It's a comment, replace with NULL for function pointers
                    if self._is_function_pointer_type(sc.ret_type):
                        lines.append("    return NULL;")
                    else:
                        lines.append(f"    return {return_value};")  # keep as-is (might cause compilation error)
                else:
                    lines.append(f"    return {return_value};")
            elif sc.ret_type == 'void':
                # void function, no return needed
                pass
            else:
                # No return value specified
                # Check if this is a function pointer type
                if self._is_function_pointer_type(sc.ret_type):
                    lines.append("    return NULL;")
                else:
                    lines.append("    return /* TODO */;")

            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    def has_stubs(self):
        """Return True if any function path has stub constraints."""
        return any(True for _ in self._iter_stubs())
