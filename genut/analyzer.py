"""C source analyzer using libclang."""

import os
import re
import clang.cindex as clang

from .models import FunctionInfo
from .extractor import ConstraintExtractor


class CSourceAnalyzer:
    """Responsible for parsing C source code with libclang and extracting function information."""

    def __init__(self, source_file, compile_args, target_funcs, project_root):
        self.source_file = os.path.realpath(source_file)
        self.compile_args = compile_args
        self.target_funcs = target_funcs
        self.project_root = os.path.realpath(project_root)
        self.known_constants = set(['true', 'false', 'nullptr', 'NULL'])

    def _extract_ordered_includes(self):
        """Extract all header files in order from the source file."""
        ordered_includes = []
        seen = set()
        try:
            with open(self.source_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Match #include <...> or #include "..."
                    match = re.match(r'^\s*#\s*include\s+([<"].+?[>"])', line)
                    if match:
                        inc = match.group(1)
                        if inc not in seen:
                            seen.add(inc)
                            ordered_includes.append(inc)
        except Exception as e:
            print(f"Warning: Regex include extraction failed: {e}")
        return ordered_includes

    def analyze(self):
        """Analyze the source file and extract function information."""
        ordered_includes = self._extract_ordered_includes()

        index = clang.Index.create()
        options = clang.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
        # Ensure include directory is present (temporary fix for test project)
        include_dir = os.path.join(self.project_root, "test_c_project/include")
        if os.path.isdir(include_dir):
            args = list(self.compile_args)
            include_arg = f"-I{include_dir}"
            if include_arg not in args:
                args.append(include_arg)
                print(f"[DEBUG] Added include path: {include_arg}")
            self.compile_args = args
        tu = index.parse(self.source_file, args=self.compile_args, options=options)

        funcs_info = []
        for node in tu.cursor.walk_preorder():
            # Collect macro definitions and enum constants
            if node.kind in (clang.CursorKind.MACRO_DEFINITION, clang.CursorKind.ENUM_CONSTANT_DECL):
                if node.spelling:
                    self.known_constants.add(node.spelling)

            elif node.kind == clang.CursorKind.FUNCTION_DECL:
                if node.location.file and os.path.realpath(node.location.file.name) == self.source_file:
                    if not node.is_definition():
                        continue

                    func_name = node.spelling
                    if not self.target_funcs or func_name in self.target_funcs:
                        ret_type = node.result_type.spelling
                        params = []
                        for arg in node.get_arguments():
                            param_name = arg.spelling if arg.spelling else f"arg_{len(params)}"
                            param_type = arg.type.spelling
                            canon_type = arg.type.get_canonical().spelling


                            params.append({
                                "name": param_name,
                                "type": param_type,
                                "canonical_type": canon_type
                            })

                        complexity = self._calculate_complexity(node)
                        info = FunctionInfo(func_name, ret_type, params, complexity)

                        extractor = ConstraintExtractor(node, params)
                        info.paths = extractor.extract_paths()
                        info.global_vars = extractor.global_vars

                        funcs_info.append(info)

        return funcs_info, ordered_includes, self.known_constants

    def _calculate_complexity(self, node):
        """Calculate complexity based on constructs the path extractor handles: if/else chains and switch cases."""
        complexity = 1
        branch_kinds = {
            clang.CursorKind.IF_STMT,
            clang.CursorKind.CASE_STMT, clang.CursorKind.DEFAULT_STMT,
        }
        for child in node.walk_preorder():
            if child.kind in branch_kinds:
                complexity += 1
        return complexity