"""Data models for UT generation."""

# Function pointer source types
FUNC_PTR_SOURCE_GLOBAL = "global"      # Global variable
FUNC_PTR_SOURCE_PARAM = "param"        # Function parameter
FUNC_PTR_SOURCE_RETURN = "return"      # Return value of another function
FUNC_PTR_SOURCE_FIELD = "field"        # Structure field
FUNC_PTR_SOURCE_LOCAL = "local"        # Local variable

class StubConstraint:
    """Describes a stub needed for one test path: which function to replace and what it should return."""
    def __init__(self, callee_name, return_value, ret_type, params, output_params=None,
                 is_function_pointer=False, pointer_var_name=None, pointer_source_type=None):
        self.callee_name = callee_name    # name of the function to stub
        self.return_value = return_value  # value the stub must return (str) - for non-void functions
        self.ret_type = ret_type          # return type of the callee
        self.params = params              # list of {'name': .., 'type': ..}
        # For void functions that modify parameters: map param_index -> (var_name, value)
        self.output_params = output_params or {}
        # Function pointer specific fields
        self.is_function_pointer = is_function_pointer  # True if this is a function pointer stub
        self.pointer_var_name = pointer_var_name        # Name of the function pointer variable
        self.pointer_source_type = pointer_source_type  # Source type: global, param, return, field, local


class PathConstraint:
    """Parameter constraints for a single test path."""
    def __init__(self, param_values=None, description="", expected_return=None,
                 stub_constraints=None):
        self.param_values = param_values or {}
        self.description = description
        self.expected_return = expected_return
        self.stub_constraints = stub_constraints or []  # list[StubConstraint]


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