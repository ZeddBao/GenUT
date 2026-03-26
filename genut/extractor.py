"""Constraint extractor from function AST."""

import re
import clang.cindex as clang

from .models import PathConstraint


class ConstraintExtractor:
    """Extract if/switch branch conditions from function AST and generate test paths with parameter constraints."""

    _OP_REVERSE = {'>': '<', '>=': '<=', '<': '>', '<=': '>=', '==': '==', '!=': '!='}

    def __init__(self, func_node, params):
        self.func_node = func_node
        self.param_names = {p['name'] for p in params}
        self.global_vars = {}
        self._find_global_vars()
        self.trackable_vars = self.param_names.union(self.global_vars.keys())

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

    def extract_paths(self):
        paths = []
        body = next((c for c in self.func_node.get_children() if c.kind == clang.CursorKind.COMPOUND_STMT), None)
        if body:
            self._visit(body, {}, paths)
        return paths or [PathConstraint()]

    def _visit(self, node, ctx, paths):
        for child in node.get_children():
            k = child.kind
            if k == clang.CursorKind.SWITCH_STMT:
                self._handle_switch(child, ctx, paths)
            elif k == clang.CursorKind.IF_STMT:
                self._handle_if(child, ctx, paths)
            else:
                self._visit(child, ctx, paths)

    def _handle_switch(self, switch_node, ctx, paths):
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
            paths.append(PathConstraint(c, desc, expected_return=ret_val))
        if has_default:
            paths.append(PathConstraint(dict(ctx), "default"))

    def _handle_if(self, if_node, ctx, paths):
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
        for cond, body in chain:
            true_ctx = self._apply_condition(cond, neg_ctx, negate=False)
            true_paths = []
            if body:
                self._visit(body, true_ctx, true_paths)
            if not true_paths:
                cond_text = ' '.join(t.spelling for t in cond.get_tokens())
                ret_val = self._get_return_value(body) if body else None
                true_paths.append(PathConstraint(true_ctx, cond_text, expected_return=ret_val))
            paths.extend(true_paths)
            neg_ctx = self._apply_condition(cond, neg_ctx, negate=True)

        if else_body is not None:
            else_paths = []
            self._visit(else_body, neg_ctx, else_paths)
            if not else_paths:
                ret_val = self._get_return_value(else_body)
                else_paths.append(PathConstraint(neg_ctx, "else", expected_return=ret_val))
            paths.extend(else_paths)

    def _apply_condition(self, cond_node, ctx, negate):
        token_str = ' '.join(t.spelling for t in cond_node.get_tokens())
        result = dict(ctx)
        _LIT = r'(-\s*\d+|[A-Za-z0-9_]+)'
        for param in self.trackable_vars:
            existing = result.get(param)
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
                    result[param] = struct_val
                    break
            else:
                hint = existing if not isinstance(existing, dict) else None
                m = re.search(rf'\b{re.escape(param)}\s*(>|>=|<|<=|==|!=)\s*{_LIT}', token_str)
                if m and m.group(2) not in self.trackable_vars:
                    result[param] = self._solve(m.group(1), m.group(2), negate, hint)
                    continue
                m = re.search(rf'{_LIT}\s*(>|>=|<|<=|==|!=)\s*\b{re.escape(param)}\b', token_str)
                if m and m.group(1) not in self.trackable_vars:
                    prefix = token_str[:m.start(1)].rstrip()
                    if not (prefix.endswith('.') or prefix.endswith('->')):
                        rev = self._OP_REVERSE.get(m.group(2), m.group(2))
                        result[param] = self._solve(rev, m.group(1), negate, hint)
        return result

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