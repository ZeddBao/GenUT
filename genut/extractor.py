"""Constraint extractor from function AST."""

import re
import clang.cindex as clang

from .models import (
    PathConstraint, StubConstraint,
    FUNC_PTR_SOURCE_GLOBAL, FUNC_PTR_SOURCE_PARAM, FUNC_PTR_SOURCE_RETURN,
    FUNC_PTR_SOURCE_FIELD, FUNC_PTR_SOURCE_LOCAL
)


class ConstraintExtractor:
    """Extract if/switch branch conditions from function AST and generate test paths with parameter constraints."""

    _OP_REVERSE = {'>': '<', '>=': '<=', '<': '>', '<=': '>=', '==': '==', '!=': '!='}

    def __init__(self, func_node, params):
        self.func_node = func_node
        self.param_names = {p['name'] for p in params}
        self.global_vars = {}
        # Function pointer detection - initialize before _find_global_vars
        self.func_ptr_vars = {}  # function pointer variable -> type info
        self.func_ptr_calls = {}  # call expression -> function pointer info
        self._find_global_vars()
        self.trackable_vars = self.param_names.union(self.global_vars.keys())
        # Maps local var name -> callee info for vars initialized from a CALL_EXPR
        self.call_var_map = {}
        self._find_call_vars()
        # Maps local var name -> callee info for vars modified via pointer parameters in a CALL_EXPR
        self.call_modified_var_map = {}
        self._find_call_modified_vars()
        self._find_func_ptr_vars()
        self._find_func_ptr_params()


    def _find_global_vars(self):
        for node in self.func_node.walk_preorder():
            if node.kind == clang.CursorKind.DECL_REF_EXPR:
                ref = node.referenced
                if ref and ref.kind == clang.CursorKind.VAR_DECL:
                    parent = ref.semantic_parent
                    if parent and parent.kind in (clang.CursorKind.TRANSLATION_UNIT, clang.CursorKind.NAMESPACE):
                        self.global_vars[node.spelling] = {
                            'type': ref.type.spelling,
                            'canonical_type': ref.type.get_canonical().spelling
                        }
                        # Also track function pointer globals
                        if self._is_function_pointer_type(ref.type):
                            pointee = self._get_func_ptr_pointee(ref.type)
                            if pointee:
                                ret_type = pointee.get_result().spelling if pointee.get_result() else "void"
                                params = []
                                try:
                                    for i, arg_type in enumerate(pointee.argument_types()):
                                        params.append({
                                            'name': f"arg{i}",
                                            'type': arg_type.spelling
                                        })
                                except Exception as e:
                                    # Silent error handling
                                    pass
                            else:
                                ret_type = "void"
                                params = []
                            self.func_ptr_vars[node.spelling] = {
                                'type': ref.type.spelling,
                                'canonical_type': ref.type.get_canonical().spelling,
                                'ret_type': ret_type,
                                'params': params,
                                'is_global': True
                            }

    def _find_call_vars(self):
        """Find local variables whose initializers are CALL_EXPR nodes (non-void return)."""
        for node in self.func_node.walk_preorder():
            if node.kind != clang.CursorKind.VAR_DECL:
                continue
            var_name = node.spelling
            # Skip params and globals — only track true locals
            if var_name in self.param_names or var_name in self.global_vars:
                continue
            call_expr = self._find_call_expr(node)
            if call_expr is None:
                continue
            callee_info = self._extract_callee_info(call_expr)
            if callee_info and callee_info.get('ret_type', 'void') != 'void':
                self.call_var_map[var_name] = callee_info

    def _find_call_modified_vars(self):
        """Find local variables modified via pointer parameters in CALL_EXPR nodes."""
        for node in self.func_node.walk_preorder():
            if node.kind != clang.CursorKind.CALL_EXPR:
                continue

            # Extract callee info
            callee_info = self._extract_callee_info(node)
            if not callee_info:
                continue

            # Check each argument for &var expressions where var is a local variable
            arg_index = 0
            children = list(node.get_children())
            for child in children:
                # Skip the callee expression (first child)
                if child == children[0]:
                    continue

                # Check if this argument is a unary & operator (passing address of a local variable)
                if child.kind == clang.CursorKind.UNARY_OPERATOR:
                    # Get the operator token
                    op_tokens = [t.spelling for t in child.get_tokens()]
                    if '&' in op_tokens:
                        # Find the variable being referenced (should be the operand child)
                        for operand in child.get_children():
                            if operand.kind == clang.CursorKind.DECL_REF_EXPR:
                                var_name = operand.spelling
                                # Store callee info and argument index
                                self.call_modified_var_map[var_name] = {
                                    'callee_info': callee_info,
                                    'arg_index': arg_index
                                }
                                # Add to trackable_vars so it can be referenced in conditions
                                self.trackable_vars.add(var_name)
                # Check if argument is a pointer parameter (passed directly)
                elif child.kind == clang.CursorKind.DECL_REF_EXPR:
                    # Check if the referenced variable is a parameter (already in trackable_vars)
                    var_name = child.spelling
                    if var_name in self.trackable_vars:
                        # Check if the type is a pointer (simple string check for '*')
                        # We need to get the type of the variable from the function parameters
                        # For now, we'll assume pointer parameters can be modified
                        # We'll store it with a flag to indicate it's a pointer param
                        self.call_modified_var_map[var_name] = {
                            'callee_info': callee_info,
                            'arg_index': arg_index,
                            'is_pointer_param': True
                        }

                arg_index += 1

    def _is_function_pointer_type(self, type_cursor):
        """Check if a type is a function pointer or function pointer array."""
        # Check for direct function pointer
        if type_cursor.kind == clang.TypeKind.POINTER:
            pointee = type_cursor.get_pointee()
            return pointee.kind == clang.TypeKind.FUNCTIONPROTO

        # Check for array of function pointers
        # Check if it's an array type (CONSTANTARRAY, INCOMPLETEARRAY, etc.)
        if type_cursor.kind in (clang.TypeKind.CONSTANTARRAY,
                                clang.TypeKind.INCOMPLETEARRAY,
                                clang.TypeKind.VARIABLEARRAY):
            # Get the element type
            element_type = type_cursor.get_array_element_type()
            # Check if element type is function pointer
            if element_type.kind == clang.TypeKind.POINTER:
                pointee = element_type.get_pointee()
                return pointee.kind == clang.TypeKind.FUNCTIONPROTO

        return False

    def _get_func_ptr_pointee(self, type_cursor):
        """Get the function prototype pointee for a function pointer type (handles arrays)."""
        if type_cursor.kind == clang.TypeKind.POINTER:
            return type_cursor.get_pointee()
        elif type_cursor.kind in (clang.TypeKind.CONSTANTARRAY,
                                  clang.TypeKind.INCOMPLETEARRAY,
                                  clang.TypeKind.VARIABLEARRAY):
            element_type = type_cursor.get_array_element_type()
            if element_type.kind == clang.TypeKind.POINTER:
                return element_type.get_pointee()
        return None

    def _find_func_ptr_vars(self):
        """Find function pointer variable declarations (global and local)."""
        for node in self.func_node.walk_preorder():
            if node.kind == clang.CursorKind.VAR_DECL:
                # Check if the variable type is a function pointer
                if self._is_function_pointer_type(node.type):
                    # Get function signature information
                    pointee = self._get_func_ptr_pointee(node.type)
                    # Extract return type
                    ret_type = pointee.get_result().spelling if pointee.get_result() else "void"
                    # Extract parameter types
                    params = []
                    try:
                        for i, arg_type in enumerate(pointee.argument_types()):
                            params.append({
                                'name': f"arg{i}",
                                'type': arg_type.spelling
                            })
                    except:
                        # Some function pointer types may not expose argument types
                        pass

                    self.func_ptr_vars[node.spelling] = {
                        'type': node.type.spelling,
                        'canonical_type': node.type.get_canonical().spelling,
                        'ret_type': ret_type,
                        'params': params,
                        'is_global': node.semantic_parent and node.semantic_parent.kind in (
                            clang.CursorKind.TRANSLATION_UNIT, clang.CursorKind.NAMESPACE
                        )
                    }
                    # Add to trackable vars if not already there
                    self.trackable_vars.add(node.spelling)

    def _find_func_ptr_params(self):
        """Find function pointer parameters in the function signature."""
        # Iterate through function parameters using libclang
        for node in self.func_node.get_children():
            if node.kind == clang.CursorKind.PARM_DECL:
                if self._is_function_pointer_type(node.type):
                    # Extract function pointer signature
                    pointee = self._get_func_ptr_pointee(node.type)
                    ret_type = pointee.get_result().spelling if pointee.get_result() else "void"
                    params = []
                    try:
                        for i, arg_type in enumerate(pointee.argument_types()):
                            params.append({'name': f"arg{i}", 'type': arg_type.spelling})
                    except:
                        pass

                    self.func_ptr_vars[node.spelling] = {
                        'type': node.type.spelling,
                        'canonical_type': node.type.get_canonical().spelling,
                        'ret_type': ret_type,
                        'params': params,
                        'is_global': False,
                        'is_param': True
                    }
                    self.trackable_vars.add(node.spelling)

    def _find_call_expr(self, node):
        """Recursively find the first CALL_EXPR child of a node."""
        for child in node.get_children():
            if child.kind == clang.CursorKind.CALL_EXPR:
                return child
            result = self._find_call_expr(child)
            if result is not None:
                return result
        return None

    def _extract_direct_func_info(self, func_decl):
        """Extract information from a direct function declaration."""
        params = [
            {'name': p.spelling or f"arg{i}", 'type': p.type.spelling}
            for i, p in enumerate(func_decl.get_arguments())
        ]
        return {
            'callee_name': func_decl.spelling,
            'ret_type': func_decl.result_type.spelling,
            'params': params,
            'is_function_pointer': False,
            'pointer_var_name': None,
            'pointer_source_type': None
        }

    def _extract_func_ptr_from_var(self, var_decl, call_expr):
        """Extract function pointer information from a variable declaration."""
        var_name = var_decl.spelling

        if var_name in self.func_ptr_vars:
            # We already have type info from _find_func_ptr_vars
            info = self.func_ptr_vars[var_name]
            # Determine source type
            if info.get('is_param', False):
                source_type = FUNC_PTR_SOURCE_PARAM
            elif info.get('is_global', False):
                source_type = FUNC_PTR_SOURCE_GLOBAL
            else:
                source_type = FUNC_PTR_SOURCE_LOCAL
            return {
                'callee_name': var_name,
                'ret_type': info['ret_type'],
                'params': info['params'],
                'is_function_pointer': True,
                'pointer_var_name': var_name,
                'pointer_source_type': source_type
            }

        # Try to extract type info directly from the variable type
        if self._is_function_pointer_type(var_decl.type):
            pointee = self._get_func_ptr_pointee(var_decl.type)
            if pointee:
                ret_type = pointee.get_result().spelling if pointee.get_result() else "void"
                params = []
                try:
                    for i, arg_type in enumerate(pointee.argument_types()):
                        params.append({'name': f"arg{i}", 'type': arg_type.spelling})
                except Exception as e:
                    # Silent error handling
                    pass
            else:
                ret_type = "void"
                params = []
            # Determine source type
            if var_decl.kind == clang.CursorKind.PARM_DECL:
                source_type = FUNC_PTR_SOURCE_PARAM
            elif var_decl.semantic_parent and var_decl.semantic_parent.kind in (
                clang.CursorKind.TRANSLATION_UNIT, clang.CursorKind.NAMESPACE
            ):
                source_type = FUNC_PTR_SOURCE_GLOBAL
            else:
                source_type = FUNC_PTR_SOURCE_LOCAL
            return {
                'callee_name': var_name,
                'ret_type': ret_type,
                'params': params,
                'is_function_pointer': True,
                'pointer_var_name': var_name,
                'pointer_source_type': source_type
            }

        return None

    def _extract_callee_info_from_expr(self, expr, call_expr):
        """Extract callee information from an arbitrary expression."""
        # Direct DECL_REF_EXPR
        if expr.kind == clang.CursorKind.DECL_REF_EXPR:
            ref = expr.referenced
            if ref:
                if ref.kind == clang.CursorKind.FUNCTION_DECL:
                    return self._extract_direct_func_info(ref)
                elif ref.kind == clang.CursorKind.VAR_DECL:
                    return self._extract_func_ptr_from_var(ref, call_expr)

        # ARRAY_SUBSCRIPT_EXPR - array element access
        elif expr.kind == clang.CursorKind.ARRAY_SUBSCRIPT_EXPR:
            # Get the array expression (e.g., global_op_array)
            children = list(expr.get_children())
            if len(children) >= 1:
                array_expr = children[0]
                # Recursively extract from the array expression
                result = self._extract_callee_info_from_expr(array_expr, call_expr)
                if result:
                    # The result is for the array itself, but we need to note it's an array element
                    result['is_array_element'] = True
                    result['array_subscript'] = True
                return result

        # UNEXPOSED_EXPR - recursively check children
        elif expr.kind == clang.CursorKind.UNEXPOSED_EXPR:
            children = list(expr.get_children())
            for child in children:
                result = self._extract_callee_info_from_expr(child, call_expr)
                if result:
                    return result

        # Check children recursively
        for child in expr.get_children():
            result = self._extract_callee_info_from_expr(child, call_expr)
            if result:
                return result

        return None

    def _extract_complex_func_ptr_expr(self, callee_expr, call_expr):
        """Handle complex function pointer expressions (dereferences, casts, etc.)."""
        return self._extract_callee_info_from_expr(callee_expr, call_expr)

    def _extract_callee_info(self, call_expr):
        """Extract callee information from a CALL_EXPR, supporting both direct functions and function pointers."""
        children = list(call_expr.get_children())
        if not children:
            return None

        callee_expr = children[0]
        # Use the new expression-based extraction
        return self._extract_callee_info_from_expr(callee_expr, call_expr)

    def extract_paths(self):
        paths = []
        body = next((c for c in self.func_node.get_children() if c.kind == clang.CursorKind.COMPOUND_STMT), None)
        if body:
            self._visit(body, {}, paths, {})
        return paths or [PathConstraint()]

    def _visit(self, node, ctx, paths, stub_ctx):
        for child in node.get_children():
            k = child.kind
            if k == clang.CursorKind.SWITCH_STMT:
                self._handle_switch(child, ctx, paths, stub_ctx)
            elif k == clang.CursorKind.IF_STMT:
                self._handle_if(child, ctx, paths, stub_ctx)
            else:
                self._visit(child, ctx, paths, stub_ctx)

    def _handle_switch(self, switch_node, ctx, paths, stub_ctx):
        children = list(switch_node.get_children())
        if not children:
            return
        switch_param = self._get_param_ref(children[0])
        seen, has_default = [], False
        for n in switch_node.walk_preorder():
            if n.kind == clang.CursorKind.CASE_STMT:
                case_children = list(n.get_children())
                if case_children:
                    val = self._get_value(case_children[0])
                    if val and val not in [v for v, _ in seen]:
                        seen.append((val, n))
            elif n.kind == clang.CursorKind.DEFAULT_STMT:
                has_default = True
        for val, case_node in seen:
            c = dict(ctx)
            if switch_param:
                c[switch_param] = val
            desc = f"{switch_param} == {val}" if switch_param else f"case {val}"
            ret_val = self._get_return_value(case_node)
            paths.append(PathConstraint(c, desc, expected_return=ret_val,
                                        stub_constraints=self._build_stub_constraints(stub_ctx)))
        if has_default:
            paths.append(PathConstraint(dict(ctx), "default",
                                        stub_constraints=self._build_stub_constraints(stub_ctx)))

    def _handle_if(self, if_node, ctx, paths, stub_ctx):
        chain = []
        else_body = None
        node = if_node
        while True:
            children = list(node.get_children())
            if not children:
                break
            cond = children[0]
            body = children[1] if len(children) > 1 else None
            chain.append((cond, body))
            if len(children) > 2:
                fb = children[2]
                if fb.kind == clang.CursorKind.IF_STMT:
                    node = fb
                else:
                    else_body = fb
                    break
            else:
                break

        neg_ctx = dict(ctx)
        neg_stub = dict(stub_ctx)
        for cond, body in chain:
            true_ctx, true_stub = self._apply_condition(cond, neg_ctx, neg_stub, negate=False)
            true_paths = []
            if body:
                self._visit(body, true_ctx, true_paths, true_stub)
            if not true_paths:
                cond_text = ' '.join(t.spelling for t in cond.get_tokens())
                ret_val = self._get_return_value(body) if body else None
                true_paths.append(PathConstraint(true_ctx, cond_text, expected_return=ret_val,
                                                  stub_constraints=self._build_stub_constraints(true_stub)))
            paths.extend(true_paths)
            neg_ctx, neg_stub = self._apply_condition(cond, neg_ctx, neg_stub, negate=True)

        if else_body is not None:
            else_paths = []
            self._visit(else_body, neg_ctx, else_paths, neg_stub)
            if not else_paths:
                ret_val = self._get_return_value(else_body)
                else_paths.append(PathConstraint(neg_ctx, "else", expected_return=ret_val,
                                                  stub_constraints=self._build_stub_constraints(neg_stub)))
            paths.extend(else_paths)

    def _build_stub_constraints(self, stub_ctx):
        """Convert stub_ctx {var_name: return_value} to a deduplicated list of StubConstraint."""
        by_callee = {}
        # Process return value constraints
        for var_name, ret_val in stub_ctx.items():
            if var_name.startswith('__outparam__'):
                continue  # handled separately
            info = self.call_var_map.get(var_name)
            if info:
                by_callee[info['callee_name']] = StubConstraint(
                    callee_name=info['callee_name'],
                    return_value=ret_val,
                    ret_type=info['ret_type'],
                    params=info['params'],
                    is_function_pointer=info.get('is_function_pointer', False),
                    pointer_var_name=info.get('pointer_var_name'),
                    pointer_source_type=info.get('pointer_source_type')
                )
        # Process output parameter constraints
        outparam_by_callee = {}
        for key, value in stub_ctx.items():
            if not key.startswith('__outparam__'):
                continue
            var_name = key[12:]  # remove '__outparam__' prefix
            info = self.call_modified_var_map.get(var_name)
            if not info:
                continue
            callee_info = info['callee_info']
            arg_index = info['arg_index']
            callee_name = callee_info['callee_name']
            if callee_name not in outparam_by_callee:
                outparam_by_callee[callee_name] = {
                    'callee_info': callee_info,
                    'output_params': {}
                }
            outparam_by_callee[callee_name]['output_params'][arg_index] = (var_name, value)

        # Merge output param constraints into StubConstraint objects
        for callee_name, data in outparam_by_callee.items():
            callee_info = data['callee_info']
            output_params = data['output_params']
            # If we already have a StubConstraint for this callee (from return value), update it
            if callee_name in by_callee:
                stub = by_callee[callee_name]
                stub.output_params = output_params
            else:
                # Create new StubConstraint with empty return_value (void functions)
                stub = StubConstraint(
                    callee_name=callee_name,
                    return_value='',  # placeholder for void functions
                    ret_type=callee_info['ret_type'],
                    params=callee_info['params'],
                    output_params=output_params,
                    is_function_pointer=callee_info.get('is_function_pointer', False),
                    pointer_var_name=callee_info.get('pointer_var_name'),
                    pointer_source_type=callee_info.get('pointer_source_type')
                )
                by_callee[callee_name] = stub

        return list(by_callee.values())

    def _parse_nested_field_access(self, param, token_str, lit_pattern):
        """Parse nested field access patterns like param->inner->field or param.inner.value.

        Returns (field_ops, operator, literal) if matched, where field_ops is a list
        of (field_name, is_pointer_access) tuples in order, or None if no match.
        """
        import re
        # Escape the parameter name for regex
        escaped_param = re.escape(param)
        # Match param followed by one or more field accesses
        # This pattern captures: param, then groups of (->field) or (.field)
        full_pattern = rf'\b{escaped_param}((?:\s*->\s*\w+|\s*\.\s*\w+)+)\s*(>|>=|<|<=|==|!=)\s*({lit_pattern})'
        match = re.search(full_pattern, token_str)
        if not match:
            return None

        field_chain_str = match.group(1)
        operator = match.group(2)
        literal = match.group(3)

        # Parse field chain string into list of (field_name, is_pointer_access) tuples
        # We need to preserve which fields are accessed via -> (pointer) vs . (direct)
        field_ops = []
        # Use regex to find all field accesses with their operators
        # Pattern matches: optional whitespace, then -> or ., then whitespace, then field name
        field_pattern = r'(\s*)(->|\.)(\s*)(\w+)'
        for m in re.finditer(field_pattern, field_chain_str):
            op = m.group(2)  # '->' or '.'
            field_name = m.group(4)
            is_pointer = (op == '->')
            field_ops.append((field_name, is_pointer))

        if not field_ops:
            return None

        return (field_ops, operator, literal)

    def _extract_field_access_from_ast(self, cond_node, param_name):
        """Extract field access information from AST node.

        Returns (field_ops, operator, literal) if the condition is a comparison
        involving a field access of the parameter, or None.
        field_ops: list of (field_name, is_pointer_access, field_type) tuples
        """
        # Debug
        # print(f"[DEBUG] _extract_field_access_from_ast called for param: {param_name}, node kind: {cond_node.kind.name}")
        # Check if this is a binary operator (comparison)
        if cond_node.kind != clang.CursorKind.BINARY_OPERATOR:
            # print(f"[DEBUG]   Not a BINARY_OPERATOR, returning None")
            return None

        # Get operator token
        op_token = None
        for token in cond_node.get_tokens():
            if token.spelling in ('>', '>=', '<', '<=', '==', '!='):
                op_token = token.spelling
                break
        if not op_token:
            return None

        # Get left and right children
        children = list(cond_node.get_children())
        if len(children) != 2:
            return None

        left, right = children
        # print(f"[DEBUG] _extract_field_access_from_ast left kind: {left.kind.name}, spelling: {left.spelling}")
        # print(f"[DEBUG] _extract_field_access_from_ast right kind: {right.kind.name}, spelling: {right.spelling}")

        # Determine which side is the field access and which is literal
        # Try to find field access on left side
        field_access = self._find_field_access_chain(left, param_name)
        if field_access:
            # Right side should be literal
            literal_tokens = [t.spelling for t in right.get_tokens() if t.spelling not in ('(', ')')]
            if literal_tokens:
                literal = ' '.join(literal_tokens)
                # Debug
                # print(f"[DEBUG] _extract_field_access_from_ast found: param={param_name}, field_access={field_access}, op={op_token}, literal={literal}")
                return (field_access, op_token, literal)

        # Try field access on right side
        field_access = self._find_field_access_chain(right, param_name)
        if field_access:
            # Left side should be literal
            literal_tokens = [t.spelling for t in left.get_tokens() if t.spelling not in ('(', ')')]
            if literal_tokens:
                literal = ' '.join(literal_tokens)
                # Reverse operator for right-side field access
                rev_op = self._OP_REVERSE.get(op_token, op_token)
                return (field_access, rev_op, literal)

        return None

    def _find_field_access_chain(self, node, expected_base_name):
        """Find a field access chain starting from expected_base_name.

        Returns list of (field_name, is_pointer_access, field_type) tuples
        or None if not found.
        """
        # Debug
        # print(f"[DEBUG] _find_field_access_chain: node kind={node.kind.name}, spelling={node.spelling}, expected={expected_base_name}")
        # Base case: check if this node references the parameter
        if node.kind == clang.CursorKind.DECL_REF_EXPR:
            if node.spelling == expected_base_name:
                return []  # Empty chain means direct parameter access

        # Check for member access: -> or .
        if node.kind == clang.CursorKind.MEMBER_REF_EXPR:
            # Debug
            # print(f"[DEBUG] MEMBER_REF_EXPR: node spelling={node.spelling}, type={node.type.spelling if node.type else None}")
            # Get the base object and member name
            children = list(node.get_children())
            # print(f"[DEBUG] MEMBER_REF_EXPR has {len(children)} children")
            # for i, child in enumerate(children):
            #     print(f"[DEBUG]   child {i}: kind={child.kind.name}, spelling={child.spelling}")
            if len(children) != 2:
                # Try alternative: maybe the member name is node.spelling, and base is the only child
                if len(children) == 1:
                    # print(f"[DEBUG]   Trying single child approach")
                    base = children[0]
                    member_name = node.spelling
                    # Recursively find chain in base
                    base_chain = self._find_field_access_chain(base, expected_base_name)
                    if base_chain is not None:
                        # Determine if this is pointer access
                        tokens = list(node.get_tokens())
                        is_pointer = False
                        for token in tokens:
                            if token.spelling == '->':
                                is_pointer = True
                                break
                            elif token.spelling == '.':
                                is_pointer = False
                                break
                        field_type = node.type.spelling if node.type else None
                        base_chain.append((member_name, is_pointer, field_type))
                        return base_chain
                return None

            base, member = children
            # Recursively find chain in base
            base_chain = self._find_field_access_chain(base, expected_base_name)
            if base_chain is None:
                return None

            # Determine if this is pointer access (->) or direct access (.)
            # Check tokens for the operator
            tokens = list(node.get_tokens())
            # Look for -> or . in tokens (skip identifiers)
            is_pointer = False
            for token in tokens:
                if token.spelling == '->':
                    is_pointer = True
                    break
                elif token.spelling == '.':
                    is_pointer = False
                    break

            # Get field type if possible
            field_type = node.type.spelling if node.type else None

            base_chain.append((member.spelling, is_pointer, field_type))
            return base_chain

        # Check for array access
        if node.kind == clang.CursorKind.ARRAY_SUBSCRIPT_EXPR:
            children = list(node.get_children())
            if len(children) != 2:
                return None

            array, index = children
            base_chain = self._find_field_access_chain(array, expected_base_name)
            if base_chain is None:
                return None

            # Add array access as a special field
            index_tokens = [t.spelling for t in index.get_tokens() if t.spelling not in ('[', ']')]
            index_str = ' '.join(index_tokens) if index_tokens else '0'
            base_chain.append((f'[{index_str}]', False, None))  # Array access
            return base_chain

        # Check for unary operator (dereference * or address-of &)
        if node.kind == clang.CursorKind.UNARY_OPERATOR:
            children = list(node.get_children())
            if len(children) != 1:
                return None

            # Check operator
            tokens = list(node.get_tokens())
            if tokens and tokens[0].spelling == '*':
                # Dereference - treat as pointer access
                base_chain = self._find_field_access_chain(children[0], expected_base_name)
                if base_chain:
                    # Add a dummy entry for dereference
                    base_chain.append(('*', True, None))
                    return base_chain

        # Handle UNEXPOSED_EXPR - may contain nested expressions
        if node.kind == clang.CursorKind.UNEXPOSED_EXPR:
            # print(f"[DEBUG] UNEXPOSED_EXPR: spelling={node.spelling}, type={node.type.spelling if node.type else None}")
            # Try to find field access in children
            children = list(node.get_children())
            # print(f"[DEBUG] UNEXPOSED_EXPR has {len(children)} children")
            for child in children:
                # print(f"[DEBUG]   child kind={child.kind.name}, spelling={child.spelling}")
                chain = self._find_field_access_chain(child, expected_base_name)
                if chain is not None:
                    # Check if this child itself is the field name (like 'data')
                    # and we need to find the base in its siblings or parent
                    if node.spelling and not chain:
                        # This might be a field name without base context
                        # Need to look at parent or siblings
                        pass
                    else:
                        return chain

        # Handle PAREN_EXPR - just recurse into child
        if node.kind == clang.CursorKind.PAREN_EXPR:
            children = list(node.get_children())
            if len(children) == 1:
                return self._find_field_access_chain(children[0], expected_base_name)

        # Generic fallback: if node has children, check them recursively
        children = list(node.get_children())
        if children:
            # print(f"[DEBUG] Generic fallback for {node.kind.name}: checking {len(children)} children")
            for child in children:
                chain = self._find_field_access_chain(child, expected_base_name)
                if chain is not None:
                    return chain

        return None

    def _apply_condition(self, cond_node, ctx, stub_ctx, negate):
        """Apply a branch condition, returning (new_ctx, new_stub_ctx)."""
        # Debug: print node kind
        # print(f"[DEBUG] _apply_condition node kind: {cond_node.kind}, name: {cond_node.kind.name}")
        token_str = ' '.join(t.spelling for t in cond_node.get_tokens())
        new_ctx = dict(ctx)
        new_stub = dict(stub_ctx)
        _LIT = r'(-\s*\d+|[A-Za-z0-9_]+)'
        all_vars = self.trackable_vars | set(self.call_var_map.keys()) | set(self.call_modified_var_map.keys())

        # Skip variables that are local call results (return values or output params)
        # They will be handled in later loops
        # But keep pointer parameters that may be modified by calls
        local_call_vars = set(self.call_var_map.keys())
        for var_name in self.call_modified_var_map:
            info = self.call_modified_var_map[var_name]
            if not info.get('is_pointer_param', False):
                local_call_vars.add(var_name)
        param_vars = self.trackable_vars - local_call_vars
        for param in param_vars:
            existing = new_ctx.get(param)

            # Helper function to set nested value in dictionary with pointer and type info
            def set_nested_value_with_ptr(d, field_ops, value, field_types=None):
                """Set value in nested dictionary, marking pointer fields with __ptr__: True
                and optionally storing field type information with __type__ key.
                field_ops: list of (field_name, is_pointer)
                field_types: optional list of type strings corresponding to each field
                """
                def is_pointer_type(type_str):
                    """Check if a type string represents a pointer type."""
                    if not type_str:
                        return False
                    # Remove const qualifier and whitespace
                    stripped = type_str.strip().replace('const ', '').replace('const', '')
                    # Check if it ends with '*'
                    return stripped.endswith('*')

                current = d
                for i, (field_name, is_pointer) in enumerate(field_ops[:-1]):
                    if field_name not in current or not isinstance(current[field_name], dict):
                        current[field_name] = {}
                    # Mark pointer fields ONLY if the field type is actually a pointer type
                    field_type = field_types[i] if field_types and i < len(field_types) else None
                    if is_pointer_type(field_type):
                        current[field_name]['__ptr__'] = True
                    # Store type information if available
                    if field_type:
                        current[field_name]['__type__'] = field_type
                    current = current[field_name]
                # Set leaf value
                leaf_field, leaf_is_pointer = field_ops[-1]
                leaf_field_type = field_types[len(field_ops)-1] if field_types and len(field_ops) <= len(field_types) else None
                # Ensure leaf field is a dict to store value and type
                if leaf_field not in current or not isinstance(current[leaf_field], dict):
                    current[leaf_field] = {}
                current[leaf_field]['value'] = value
                # Mark leaf pointer ONLY if the leaf field type is actually a pointer type
                if is_pointer_type(leaf_field_type):
                    current[leaf_field]['__ptr__'] = True
                # Store leaf field type if available
                if leaf_field_type:
                    current[leaf_field]['__type__'] = leaf_field_type

            # Helper function to get nested value from dictionary
            def get_nested_value(d, field_ops):
                """Get value from nested dictionary d[field_ops[0]]...[field_ops[-1]] or None"""
                current = d
                for field_name, _ in field_ops:
                    if not isinstance(current, dict) or field_name not in current:
                        return None
                    current = current[field_name]
                # If leaf is a dict with 'value' key, return the value
                if isinstance(current, dict) and 'value' in current:
                    return current['value']
                return current

            # First try AST-based field access extraction
            ast_result = self._extract_field_access_from_ast(cond_node, param)
            if ast_result:
                field_ops_with_type, op, lit = ast_result
                # Convert to (field_name, is_pointer) format for compatibility
                field_ops = [(fname, is_ptr) for fname, is_ptr, _ in field_ops_with_type]
                # Extract type information
                field_types = [ftype for _, _, ftype in field_ops_with_type]
                if lit in self.trackable_vars:
                    # Literal is another variable, skip for now
                    pass
                else:
                    # Build nested dictionary structure
                    struct_val = existing if isinstance(existing, dict) else {}
                    # Ensure struct_val is a dict (might be a scalar from previous constraint)
                    if not isinstance(struct_val, dict):
                        struct_val = {}

                    hint = get_nested_value(struct_val, field_ops)
                    solved_value = self._solve(op, lit, negate, hint)

                    # Create a copy to avoid modifying existing dict in ctx
                    struct_val = dict(struct_val) if isinstance(struct_val, dict) else {}
                    set_nested_value_with_ptr(struct_val, field_ops, solved_value, field_types)
                    new_ctx[param] = struct_val
                    continue  # Move to next parameter

            # Fallback to regex-based nested field access (e.g., param->inner->field, param.inner.value)
            result = self._parse_nested_field_access(param, token_str, _LIT)
            if result:
                field_ops, op, lit = result
                if lit in self.trackable_vars:
                    # Literal is another variable, skip for now
                    pass
                else:
                    # Build nested dictionary structure
                    struct_val = existing if isinstance(existing, dict) else {}
                    # Ensure struct_val is a dict (might be a scalar from previous constraint)
                    if not isinstance(struct_val, dict):
                        struct_val = {}

                    hint = get_nested_value(struct_val, field_ops)
                    solved_value = self._solve(op, lit, negate, hint)

                    # Create a copy to avoid modifying existing dict in ctx
                    struct_val = dict(struct_val) if isinstance(struct_val, dict) else {}
                    set_nested_value_with_ptr(struct_val, field_ops, solved_value, None)
                    new_ctx[param] = struct_val
                    continue  # Move to next parameter

            # Fallback to single-level field access (for backward compatibility)
            matched = False
            for arrow in (r'->', r'\.'):
                m = re.search(rf'\b{re.escape(param)}\s*{arrow}\s*(\w+)\s*(>|>=|<|<=|==|!=)\s*{_LIT}', token_str)
                if m:
                    field, op, lit = m.group(1), m.group(2), m.group(3)
                    if lit in self.trackable_vars:
                        break
                    struct_val = existing if isinstance(existing, dict) else {}
                    hint = struct_val.get(field)
                    struct_val = dict(struct_val)
                    struct_val[field] = self._solve(op, lit, negate, hint)
                    new_ctx[param] = struct_val
                    matched = True
                    break
            if matched:
                continue

            # No field access, treat as scalar parameter
            hint = existing if not isinstance(existing, dict) else None
            m = re.search(rf'\b{re.escape(param)}\s*(>|>=|<|<=|==|!=)\s*{_LIT}', token_str)
            if m and m.group(2) not in self.trackable_vars:
                new_ctx[param] = self._solve(m.group(1), m.group(2), negate, hint)
                continue
            m = re.search(rf'{_LIT}\s*(>|>=|<|<=|==|!=)\s*\b{re.escape(param)}\b', token_str)
            if m and m.group(1) not in self.trackable_vars:
                prefix = token_str[:m.start(1)].rstrip()
                if not (prefix.endswith('.') or prefix.endswith('->')):
                    rev = self._OP_REVERSE.get(m.group(2), m.group(2))
                    new_ctx[param] = self._solve(rev, m.group(1), negate, hint)

        # Handle call-result local variables -> stub constraints
        for var_name in self.call_var_map:
            existing = new_stub.get(var_name)
            hint = existing if not isinstance(existing, dict) else None
            m = re.search(rf'\b{re.escape(var_name)}\s*(>|>=|<|<=|==|!=)\s*{_LIT}', token_str)
            if m and m.group(2) not in all_vars:
                new_stub[var_name] = self._solve(m.group(1), m.group(2), negate, hint)
                continue
            m = re.search(rf'{_LIT}\s*(>|>=|<|<=|==|!=)\s*\b{re.escape(var_name)}\b', token_str)
            if m and m.group(1) not in all_vars:
                prefix = token_str[:m.start(1)].rstrip()
                if not (prefix.endswith('.') or prefix.endswith('->')):
                    rev = self._OP_REVERSE.get(m.group(2), m.group(2))
                    new_stub[var_name] = self._solve(rev, m.group(1), negate, hint)

        # Handle output parameter variables -> stub constraints
        for var_name, info in self.call_modified_var_map.items():
            existing = new_stub.get(var_name)
            hint = existing if not isinstance(existing, dict) else None
            m = re.search(rf'\b{re.escape(var_name)}\s*(>|>=|<|<=|==|!=)\s*{_LIT}', token_str)
            if m and m.group(2) not in all_vars:
                # Store as output param constraint with special key
                new_stub[f"__outparam__{var_name}"] = self._solve(m.group(1), m.group(2), negate, hint)
                continue
            m = re.search(rf'{_LIT}\s*(>|>=|<|<=|==|!=)\s*\b{re.escape(var_name)}\b', token_str)
            if m and m.group(1) not in all_vars:
                prefix = token_str[:m.start(1)].rstrip()
                if not (prefix.endswith('.') or prefix.endswith('->')):
                    rev = self._OP_REVERSE.get(m.group(2), m.group(2))
                    new_stub[f"__outparam__{var_name}"] = self._solve(rev, m.group(1), negate, hint)

        return new_ctx, new_stub

    def _solve(self, op, literal, negate, hint=None):
        try:
            n = int(literal.replace(' ', ''), 0)
        except (ValueError, TypeError):
            return literal if not negate else f"/* not {literal} */"
        if negate and op == '==' and hint is not None:
            try:
                h = int(str(hint).replace(' ', ''), 0)
                return str(n - 1) if h <= n else str(n + 1)
            except (ValueError, TypeError):
                pass
        table = {
            False: {'>': n+1, '>=': n,   '<': n-1, '<=': n,   '==': n,   '!=': n+1},
            True:  {'>': n,   '>=': n-1, '<': n,   '<=': n+1, '==': n+1, '!=': n  },
        }
        return str(table[negate].get(op, n))

    def _get_return_value(self, node):
        if node is None:
            return None
        for child in node.walk_preorder():
            if child.kind == clang.CursorKind.RETURN_STMT:
                toks = [t.spelling for t in child.get_tokens()]
                expr_toks = [t for t in toks if t not in ('return', ';')]
                if not expr_toks:
                    return None
                expr = ' '.join(expr_toks)
                expr = re.sub(r'-\s+(\d)', r'-\1', expr)
                return expr
        return None

    def _get_param_ref(self, node):
        if node.kind == clang.CursorKind.DECL_REF_EXPR and node.spelling in self.trackable_vars:
            return node.spelling
        for child in node.get_children():
            r = self._get_param_ref(child)
            if r:
                return r
        return None

    def _get_value(self, node):
        if node.kind == clang.CursorKind.INTEGER_LITERAL:
            toks = list(node.get_tokens())
            return toks[0].spelling if toks else None
        if node.kind == clang.CursorKind.DECL_REF_EXPR:
            return node.spelling
        for child in node.get_children():
            v = self._get_value(child)
            if v:
                return v
        return None
