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
                    yield func, i, sc

    def stub_func_name(self, callee_name, func_name, path_index):
        """Canonical stub function name."""
        return f"stub_{callee_name}_{func_name}_{path_index}"

    def build_stub_declarations(self):
        """Return a list of declaration strings to embed in the .h file."""
        seen = set()
        decls = []
        for func, i, sc in self._iter_stubs():
            name = self.stub_func_name(sc.callee_name, func.name, i)
            if name in seen:
                continue
            seen.add(name)
            if sc.params:
                param_str = ", ".join(f"{p['type']} {p['name']}" for p in sc.params)
            else:
                param_str = "void"
            decls.append(f"{sc.ret_type} {name}({param_str});")
        return decls

    def build_stub_cpp(self):
        """Generate the full content of the _stub.cpp file."""
        lines = []
        # Add copyright header if configured
        lines.extend(self._build_copyright_header())
        if self.config.copyright_header:
            lines.append("")
        lines.append("// --- Auto-generated Stub Implementations ---")
        lines.append(f'#include "{self.out_base_name}.h"')
        lines.append("")

        seen = set()
        for func, i, sc in self._iter_stubs():
            name = self.stub_func_name(sc.callee_name, func.name, i)
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
                param_str = ", ".join(f"{p['type']} {p['name']}" for p in sc.params)
            else:
                param_str = "void"
            lines.append(f"{sc.ret_type} {name}({param_str}) {{")

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
                lines.append(f"    return {sc.return_value};")
            elif sc.ret_type == 'void':
                # void function, no return needed
                pass
            else:
                lines.append("    return /* TODO */;")

            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    def has_stubs(self):
        """Return True if any function path has stub constraints."""
        return any(True for _ in self._iter_stubs())
