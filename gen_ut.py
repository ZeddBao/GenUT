#!/usr/bin/env python3
"""Entry script for C UT generation with configurable architecture.

This script serves as the main entry point for generating GTest unit tests
from C source files using libclang. It uses the modular architecture with
configuration injection for decoupling project-specific customizations.
"""

import sys
import os
import argparse

from genut.compdb import CompDbParser
from genut.analyzer import CSourceAnalyzer
from genut.builder import GTestBuilder
from genut.models import PathConstraint, FunctionInfo
from genut.config import GeneratorConfig


class UTGeneratorApp:
    """Main application class for generating unit tests."""

    def __init__(self, args):
        self.compdb_path = args.compdb
        self.source_file = args.src
        self.target_funcs = [f.strip() for f in args.funcs.split(';') if f.strip()]
        self.outdir = args.outdir
        self.construct = args.construct

        if args.project_root:
            self.project_root = os.path.abspath(args.project_root)
        else:
            self.project_root = os.getcwd()

        # Load configuration if provided
        if args.config:
            self.config = GeneratorConfig.from_file(args.config)
        else:
            self.config = GeneratorConfig.default()

        # Override compiler if specified
        if args.compiler != "auto":
            self.config.compiler = args.compiler

    def run(self):
        """Run the UT generation pipeline."""
        print(f"Project root set to: {self.project_root}")
        print(f"Loading compilation database from: {self.compdb_path}")

        # Initialize compilation database parser with config
        parser = CompDbParser(self.compdb_path, compiler=self.config.compiler)
        compile_args = parser.get_args_for_file(self.source_file)

        print(f"Parsing source file: {self.source_file}")
        analyzer = CSourceAnalyzer(
            self.source_file,
            compile_args,
            self.target_funcs,
            self.project_root
        )
        funcs_info, project_includes, known_constants = analyzer.analyze()

        if not funcs_info:
            if self.target_funcs:
                print(f"No matching functions found for: {', '.join(self.target_funcs)}")
            else:
                print("No function definitions found in the source file.")
            sys.exit(1)

        if not self.construct:
            for func in funcs_info:
                func.paths = [PathConstraint() for _ in range(func.complexity)]

        print(f"Found {len(funcs_info)} matching function(s). Generating GTest code...")

        builder = GTestBuilder(
            source_file=self.source_file,
            funcs_info=funcs_info,
            known_constants=known_constants,
            config=self.config,
            outdir=self.outdir,
            project_includes=project_includes,
            construct=self.construct
        )

        h_code = builder.build_header()
        cpp_code = builder.build_cpp()

        self._write_output(builder.out_h_path, h_code)
        self._write_output(builder.out_cpp_path, cpp_code)

    def _write_output(self, file_path, content):
        """Write generated code to file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully wrote: {file_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate GTest UT framework using compile_commands.json and libclang."
    )
    parser.add_argument(
        "--compdb", required=True,
        help="Path to compile_commands.json"
    )
    parser.add_argument(
        "--src", required=True,
        help="Path to the C source file"
    )
    parser.add_argument(
        "--funcs", required=False, default="",
        help="Semicolon-separated list of target functions. Leave empty for all."
    )
    parser.add_argument(
        "--outdir", required=False, default=None,
        help="Output directory for generated files. Defaults to the source file's directory."
    )
    parser.add_argument(
        "--construct", action="store_true", default=False,
        help="Construct test parameters from branch conditions."
    )
    parser.add_argument(
        "--project-root", required=False, default=None,
        help="Explicitly specify the project root directory to correctly identify internal headers."
    )
    parser.add_argument(
        "--config", "-c", required=False, default=None,
        help="Path to JSON configuration file for customizing naming, defaults, etc."
    )
    parser.add_argument(
        "--compiler", required=False, default="auto", choices=["auto", "gcc", "clang"],
        help="Compiler to use for system include detection (auto, gcc, or clang)."
    )

    args = parser.parse_args()
    app = UTGeneratorApp(args)
    app.run()


if __name__ == "__main__":
    main()