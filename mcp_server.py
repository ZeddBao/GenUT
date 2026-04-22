#!/usr/bin/env python3
"""
FastMcp server for generating unit tests from C source files.

This MCP server wraps the gen_ut functionality, making it available as tools
that can be called by Claude agents.

Install dependencies:
    pip install fastmcp

Run server:
    python mcp_server.py
"""

import os
import sys
from typing import Optional

try:
    from fastmcp import FastMCP
except ImportError:
    print("Error: fastmcp is not installed. Install it with: pip install fastmcp")
    sys.exit(1)

from genut.analyzer import CSourceAnalyzer
from genut.builder import GTestBuilder
from genut.config import GeneratorConfig
from genut.compdb import CompDbParser
from genut.models import PathConstraint
from genut.stub_builder import StubBuilder
from genut.stub_framework import get_stub_framework

# Create FastMCP instance
mcp = FastMCP("genut-server")


@mcp.tool()
def generate_tests(
    source_file: str,
    compdb: str,
    functions: Optional[str] = None,
    outdir: Optional[str] = None,
    construct: bool = True,
    stub_framework: Optional[str] = None,
    config_file: Optional[str] = None,
    project_root: Optional[str] = None
) -> dict:
    """
    Generate unit tests for specified functions in a C source file.

    Args:
        source_file: Path to the C source file
        compdb: Path to compilation database (compile_commands.json)
        functions: Semicolon-separated list of function names to generate tests for.
                  If omitted, generates tests for all functions.
        outdir: Output directory for generated test files (default: same as source)
        construct: Whether to generate constructed test cases with parameter values
        stub_framework: Stub framework type (e.g., 'macro')
        config_file: Path to configuration JSON file (utgen.json)
        project_root: Project root directory for include path resolution

    Returns:
        Dictionary with generation results and output file paths
    """
    try:
        # Resolve paths
        source_file = os.path.abspath(source_file)
        compdb = os.path.abspath(compdb)

        if not os.path.isfile(source_file):
            return {"error": f"Source file not found: {source_file}"}
        if not os.path.isfile(compdb):
            return {"error": f"Compilation database not found: {compdb}"}

        if project_root is None:
            project_root = os.path.dirname(compdb)
        else:
            project_root = os.path.abspath(project_root)

        if outdir is None:
            outdir = os.path.dirname(source_file)
        else:
            outdir = os.path.abspath(outdir)
            os.makedirs(outdir, exist_ok=True)

        # Load configuration
        if config_file:
            config_file = os.path.abspath(config_file)
            if not os.path.isfile(config_file):
                return {"error": f"Config file not found: {config_file}"}
            config = GeneratorConfig.from_file(config_file)
        else:
            config = GeneratorConfig()

        # Parse compilation database
        parser = CompDbParser(compdb)
        compile_args = parser.get_args_for_file(source_file)

        # Analyze source file
        target_funcs = {name.strip() for name in functions.split(';')} if functions else None
        analyzer = CSourceAnalyzer(source_file, compile_args, target_funcs, project_root)
        funcs_info, project_includes, known_constants = analyzer.analyze()

        if not funcs_info:
            if target_funcs:
                return {"error": f"No matching functions found for: {', '.join(target_funcs)}"}
            return {"error": "No function definitions found in the source file."}

        if not construct:
            for func in funcs_info:
                func.paths = [PathConstraint() for _ in range(func.complexity)]

        # Setup stub framework if requested
        stub_fw = None
        stub_bld = None
        if stub_framework:
            stub_fw = get_stub_framework(stub_framework)
            stub_bld = StubBuilder(source_file, funcs_info, config, outdir)

        # Generate test code
        builder = GTestBuilder(
            source_file, funcs_info, known_constants, config,
            outdir=outdir,
            project_includes=project_includes,
            construct=construct,
            stub_framework=stub_fw,
            stub_builder=stub_bld
        )

        # Write output files
        with open(builder.out_h_path, "w") as f:
            f.write(builder.build_header())

        with open(builder.out_cpp_path, "w") as f:
            f.write(builder.build_cpp())

        stub_files = []
        if stub_bld and stub_bld.has_stubs():
            with open(stub_bld.out_stub_cpp_path, "w") as f:
                f.write(stub_bld.build_stub_cpp())
            stub_files.append(stub_bld.out_stub_cpp_path)

        return {
            "success": True,
            "source_file": source_file,
            "functions_generated": len(funcs_info),
            "function_names": [f.name for f in funcs_info],
            "output_files": {
                "header": builder.out_h_path,
                "implementation": builder.out_cpp_path,
                "stubs": stub_files
            },
            "total_test_paths": sum(len(f.paths) for f in funcs_info),
            "test_paths_per_function": {
                f.name: len(f.paths) for f in funcs_info
            }
        }

    except Exception as e:
        return {
            "error": f"Test generation failed: {str(e)}",
            "type": type(e).__name__
        }


def main():
    """Run the FastMcp server."""
    print("Starting genut MCP server...")
    print("Available tools:")
    print("  - generate_tests: Generate GTest unit tests for C functions")
    print("\nServer is ready for connections.")

    mcp.run()


if __name__ == "__main__":
    main()
