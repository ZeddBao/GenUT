"""Constraint extractor from function AST."""

import re
import clang.cindex as clang

from .models import PathConstraint, StubConstraint


class ConstraintExtractor:
    """Extract if/switch branch conditions from function AST and generate test paths with parameter constraints."""

    _OP_REVERSE = {'>': '<', '>=': '<=', '<': '>', '<=': '>=', '==': '==', '!=': '!='}

    def __init__(self, func_node, params):
        self.func_node = func_node
        self.param_names = {p['name'] for p in params}
        self.global_vars = {}
        self._find_global_vars()
        self.trackable_vars = self.param_names.union(self.global_vars.keys())
        # Maps local var name -> callee info for vars initialized from a CALL_EXPR
        self.call_var_map = {}
        self._find_call_vars()
        # Maps local var name -> callee info for vars modified via pointer parameters in a CALL_EXPR
        self.call_modified_var_map = {}
        self._find_call_modified_vars()

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

    def _find_call_vars(self):
        """Find local variables whose initializers are CALL_EXPR nodes (non-void return)."""
        for node in self.func_node.walk_preorder():
            if node.kind != clang.CursorKind.VAR_DECL:
                continue
            # Skip params and globals — only track true locals
            if node.spelling in self.param_names or node.spelling in self.global_vars:
                continue
            call_expr = self._find_call_expr(node)
            if call_expr is None:
                continue
            callee_info = self._extract_callee_info(call_expr)
            if callee_info and callee_info.get('ret_type', 'void') != 'void':
                self.call_var_map[node.spelling] = callee_info

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

    def _find_call_expr(self, node):
        """Recursively find the first CALL_EXPR child of a node."""
        for child in node.get_children():
            if child.kind == clang.CursorKind.CALL_EXPR:
                return child
            result = self._find_call_expr(child)
            if result is not None:
                return result
        return None

    def _extract_callee_info(self, call_expr):
        """Extract callee name, return type, and parameter list from a CALL_EXPR cursor."""
        for child in call_expr.walk_preorder():
            if child.kind == clang.CursorKind.DECL_REF_EXPR:
                ref = child.referenced
                if ref and ref.kind == clang.CursorKind.FUNCTION_DECL:
                    params = [
                        {'name': p.spelling or f"arg{i}", 'type': p.type.spelling}
                        for i, p in enumerate(ref.get_arguments())
                    ]
                    return {
                        'callee_name': ref.spelling,
                        'ret_type': ref.result_type.spelling,
                        'params': params,
                    }
        return None

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
                    output_params=output_params
                )
                by_callee[callee_name] = stub

        return list(by_callee.values())

    def _apply_condition(self, cond_node, ctx, stub_ctx, negate):
        """Apply a branch condition, returning (new_ctx, new_stub_ctx)."""
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
                    break
            else:
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
