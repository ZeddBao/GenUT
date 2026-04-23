"""Compilation database parser with compiler auto-detection."""

import os
import subprocess
import json
import shlex


class CompDbParser:
    """Responsible for extracting compilation arguments from compile_commands.json."""

    def __init__(self, compdb_path, compiler="auto"):
        self.compdb_path = compdb_path
        self.compdb_dir = os.path.dirname(os.path.abspath(compdb_path)) or "."
        self.compiler = compiler
        self._detected_compiler = None

    def _detect_compiler(self):
        """Detect compiler from compile_commands.json."""
        if self._detected_compiler:
            return self._detected_compiler

        try:
            compdb_dir = os.path.dirname(os.path.abspath(self.compdb_path)) or "."
            compdb_path = os.path.join(compdb_dir, "compile_commands.json")

            with open(compdb_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data and 'command' in data[0]:
                # Parse command to find compiler
                cmd_parts = data[0]['command'].split()
                if cmd_parts:
                    compiler_path = cmd_parts[0]
                    compiler_name = os.path.basename(compiler_path).lower()
                    if 'clang' in compiler_name:
                        self._detected_compiler = 'clang'
                    elif 'gcc' in compiler_name or 'g++' in compiler_name or 'cc' in compiler_name:
                        self._detected_compiler = 'gcc'
                    else:
                        self._detected_compiler = 'gcc'  # Default fallback
            elif data and 'arguments' in data[0]:
                cmd_parts = data[0]['arguments']
                if cmd_parts:
                    compiler_path = cmd_parts[0]
                    compiler_name = os.path.basename(compiler_path).lower()
                    if 'clang' in compiler_name:
                        self._detected_compiler = 'clang'
                    elif 'gcc' in compiler_name or 'g++' in compiler_name or 'cc' in compiler_name:
                        self._detected_compiler = 'gcc'
                    else:
                        self._detected_compiler = 'gcc'
        except Exception:
            self._detected_compiler = 'gcc'  # Default fallback

        return self._detected_compiler

    def _get_system_includes(self):
        """Get system include paths from compiler."""
        includes = []
        compiler = self.compiler
        if compiler == "auto":
            compiler = self._detect_compiler()

        try:
            devnull = 'NUL' if os.name == 'nt' else '/dev/null'
            cmd = [compiler, '-E', '-v', '-xc', devnull]

            result = subprocess.run(
                cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                text=True, check=False
            )

            in_include_section = False
            for line in result.stderr.splitlines():
                if line.startswith('#include "..." search starts here:'):
                    continue
                elif line.startswith('#include <...> search starts here:'):
                    in_include_section = True
                    continue
                elif line.startswith('End of search list.'):
                    in_include_section = False
                    continue

                if in_include_section:
                    path = line.strip()
                    if "(framework directory)" in path:
                        path = path.replace("(framework directory)", "").strip()
                    if os.path.isdir(path):
                        includes.append(f"-isystem{path}")
        except Exception:
            pass

        return includes

    def _expand_response_files(self, args):
        """Expand response files (arguments starting with '@') in args list."""
        expanded = []
        for arg in args:
            if arg.startswith('@'):
                resp_file = arg[1:]
                if not os.path.isabs(resp_file):
                    # Make relative to compilation database directory
                    resp_file = os.path.join(self.compdb_dir, resp_file)
                try:
                    with open(resp_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Use shlex to properly split while preserving quotes
                        expanded.extend(shlex.split(content))
                except Exception as e:
                    print(f"Warning: Failed to expand response file {resp_file}: {e}")
                    expanded.append(arg)  # Keep original argument
            else:
                expanded.append(arg)
        return expanded

    def get_args_for_file(self, source_file):
        """Get compilation arguments for a specific source file."""
        import clang.cindex as clang

        args = []
        try:
            compdb = clang.CompilationDatabase.fromDirectory(self.compdb_dir)
            commands = compdb.getCompileCommands(os.path.abspath(source_file))
            if commands:
                raw_args = list(commands[0].arguments)[1:]
                src_basename = os.path.basename(source_file)
                skip_next = False
                for arg in raw_args:
                    if skip_next:
                        skip_next = False
                        continue
                    if arg == "-c" or arg == "-o":
                        skip_next = (arg == "-o")
                        continue
                    if os.path.basename(arg) == src_basename:
                        continue
                    args.append(arg)
        except clang.CompilationDatabaseError:
            pass

        # Remove the end-of-options '--' marker and everything after it.
        # Some build systems (e.g., Clang's CMake integration on Windows) embed '--'
        # before implicit system include paths. libclang treats every argument after
        # '--' as a linker input rather than a compiler flag, which silently drops
        # any '-I' paths appended later and causes type resolution failures.
        # System includes after '--' are redundant because _get_system_includes()
        # already discovers them via the local compiler.
        if '--' in args:
            args = args[:args.index('--')]

        args.extend(self._get_system_includes())
        # Expand response files
        args = self._expand_response_files(args)
        return args