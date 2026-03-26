"""Data models for UT generation."""


class PathConstraint:
    """Parameter constraints for a single test path."""
    def __init__(self, param_values=None, description="", expected_return=None):
        self.param_values = param_values or {}
        self.description = description
        self.expected_return = expected_return


class FunctionInfo:
    """Stores extracted function information."""
    def __init__(self, name, ret_type, params, complexity):
        self.name = name
        self.ret_type = ret_type
        self.params = params
        self.complexity = complexity
        self.paths = []
        # Store global variables this function depends on
        # {name: {'type': type_str, 'canonical_type': canon_type_str}}
        self.global_vars = {}

    def get_declaration(self):
        """Generate C language declaration for the function."""
        if not self.params:
            param_str = "void"
        else:
            param_str = ", ".join([f"{p['type']} {p['name']}" for p in self.params])
        return f"{self.ret_type} {self.name}({param_str});"