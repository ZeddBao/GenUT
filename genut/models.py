"""Data models for UT generation."""


class _NonNullSentinel:
    """Sentinel meaning 'a non-NULL pointer value is required here'.

    Flows from ConstraintExtractor (where the pointer != NULL condition is
    resolved) through PathConstraint.param_values / StubConstraint.return_value
    into GTestBuilder / StubBuilder.  Consumers detect it with ``is NON_NULL``
    (identity check) so there is zero risk of collision with any real source
    value.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "NON_NULL"

    def __str__(self):
        return "NON_NULL"


# Singleton sentinel — use ``is NON_NULL`` to test, never ``== "(void*)1"``
NON_NULL = _NonNullSentinel()


# Function pointer source types
FUNC_PTR_SOURCE_GLOBAL = "global"      # Global variable
FUNC_PTR_SOURCE_PARAM = "param"        # Function parameter
FUNC_PTR_SOURCE_RETURN = "return"      # Return value of another function
FUNC_PTR_SOURCE_FIELD = "field"        # Structure field
FUNC_PTR_SOURCE_LOCAL = "local"        # Local variable

class StubConstraint:
    """Describes a stub needed for one test path: which function to replace and what it should return."""
    def __init__(self, callee_name, return_value, ret_type, params, output_params=None,
                 is_function_pointer=False, pointer_var_name=None, pointer_source_type=None,
                 array_index=None):
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
        self.array_index = array_index    # Element index string when FP is inside an array (e.g. '2')


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
        # If type ends with *, don't add space between type and name
        param_type_stripped = param_type.rstrip()
        if param_type_stripped.endswith('*'):
            return f"{param_type_stripped}{param_name}"
        return f"{param_type_stripped} {param_name}"

    def get_declaration(self):
        """Generate C language declaration for the function."""
        if not self.params:
            param_str = "void"
        else:
            param_parts = []
            for p in self.params:
                param_type = p['type']
                param_name = p['name']
                param_parts.append(self._format_param_type(param_type, param_name))
            param_str = ", ".join(param_parts)

        # Check if return type is a function pointer (contains "(*)" )
        if "(*)" in self.ret_type:
            # Function returning a function pointer: format as "int (*func_name(params))(func_params)"
            # Replace "(*)" with "(*{self.name}({param_str}))"
            # Example: "int (*)(int, int)" -> "int (*get_operation(char op))(int, int)"
            return self.ret_type.replace("(*)", f"(*{self.name}({param_str}))") + ";"
        else:
            # Normal function declaration
            return f"{self.ret_type} {self.name}({param_str});"