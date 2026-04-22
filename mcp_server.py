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

import json
import os
import sys
from pathlib import Path
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
from genut.extractor import ConstraintExtractor
from genut.models import FunctionInfo
from genut.stub_builder import StubBuilder
from genut.stub_framework import StubFramework

# Create FastMCP instance
mcp = FastMCP("genut-server")


@mcp.tool()
def list_functions(
    source_file: str,
    compdb: Optional[str] = None,
    project_root: Optional[str] = None
) -> dict:
    """
    List all functions in a C source file with their complexity metrics.

    Args:
        source_file: Path to the C source file to analyze
        compdb: Path to compilation database (compile_commands.json)
        project_root: Project root directory for relative path resolution

    Returns:
        Dictionary containing list of functions and their metadata
    """
    try:
        source_file = os.path.abspath(source_file)
        if not os.path.isfile(source_file):
            return {"error": f"Source file not found: {source_file}"}

        # Parse compilation database if provided
        compile_args = []
        if compdb:
            compdb = os.path.abspath(compdb)
            parser = CompDbParser(compdb)
            compile_args = parser.get_args_for_file(source_file)

        # Analyze source file
        analyzer = CSourceAnalyzer(source_file, compile_args=compile_args)
        funcs = analyzer.extract_functions()

        functions = []
        for func in funcs:
            functions.append({
                "name": func.name,
                "return_type": func.ret_type,
                "parameters": [
                    {
                        "name": p["name"],
                        "type": p["type"],
                        "canonical_type": p["canonical_type"]
                    }
                    for p in func.params
                ],
                "cyclomatic_complexity": func.complexity,
                "global_vars": list(func.global_vars.keys()),
            })

        return {
            "file": source_file,
            "functions": functions,
            "count": len(functions)
        }
    except Exception as e:
        return {"error": f"Failed to list functions: {str(e)}"}


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
        project_includes = parser.get_includes_for_file(source_file, project_root)

        # Analyze source file
        analyzer = CSourceAnalyzer(source_file, compile_args=compile_args)
        all_funcs = analyzer.extract_functions()
        known_constants = analyzer.known_constants

        # Filter functions if specified
        if functions:
            func_names = {name.strip() for name in functions.split(';')}
            funcs_info = [f for f in all_funcs if f.name in func_names]
            if not funcs_info:
                return {
                    "error": f"No matching functions found. Available: {[f.name for f in all_funcs]}"
                }
        else:
            funcs_info = all_funcs

        # Extract constraints for each function
        for func in funcs_info:
            try:
                extractor = ConstraintExtractor(func.node, func.params)
                func.paths = extractor.extract_paths()
                func.global_vars = extractor.global_vars
            except Exception as e:
                return {
                    "error": f"Failed to extract constraints for {func.name}: {str(e)}"
                }

        # Setup stub framework if requested
        stub_fw = None
        stub_bld = None
        if stub_framework:
            stub_fw = StubFramework(stub_framework, config)
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


@mcp.tool()
def analyze_function(
    source_file: str,
    compdb: str,
    function_name: str,
    project_root: Optional[str] = None
) -> dict:
    """
    Analyze a specific function and show its structure and constraints.

    Args:
        source_file: Path to the C source file
        compdb: Path to compilation database
        function_name: Name of the function to analyze
        project_root: Project root directory for include path resolution

    Returns:
        Dictionary with detailed function analysis
    """
    try:
        source_file = os.path.abspath(source_file)
        compdb = os.path.abspath(compdb)

        if not os.path.isfile(source_file):
            return {"error": f"Source file not found: {source_file}"}
        if not os.path.isfile(compdb):
            return {"error": f"Compilation database not found: {compdb}"}

        # Parse compilation database
        parser = CompDbParser(compdb)
        compile_args = parser.get_args_for_file(source_file)

        # Analyze source file
        analyzer = CSourceAnalyzer(source_file, compile_args=compile_args)
        all_funcs = analyzer.extract_functions()

        # Find the function
        func = next((f for f in all_funcs if f.name == function_name), None)
        if not func:
            return {
                "error": f"Function '{function_name}' not found",
                "available_functions": [f.name for f in all_funcs]
            }

        # Extract constraints
        extractor = ConstraintExtractor(func.node, func.params)
        paths = extractor.extract_paths()
        func.paths = paths
        func.global_vars = extractor.global_vars

        # Build analysis result
        result = {
            "name": func.name,
            "return_type": func.ret_type,
            "cyclomatic_complexity": func.complexity,
            "parameters": [
                {
                    "name": p["name"],
                    "type": p["type"],
                    "canonical_type": p["canonical_type"]
                }
                for p in func.params
            ],
            "global_variables": func.global_vars,
            "test_paths": len(paths),
            "paths": []
        }

        # Add path details
        for i, path in enumerate(paths, 1):
            path_info = {
                "index": i,
                "description": path.description,
                "expected_return": path.expected_return,
                "parameter_values": {}
            }

            # Clean up parameter values for display
            for param_name, param_val in path.param_values.items():
                if isinstance(param_val, dict):
                    path_info["parameter_values"][param_name] = f"<struct with {len(param_val)} fields>"
                else:
                    path_info["parameter_values"][param_name] = str(param_val)

            result["paths"].append(path_info)

        return result

    except Exception as e:
        return {
            "error": f"Function analysis failed: {str(e)}",
            "type": type(e).__name__
        }


def main():
    """Run the FastMcp server."""
    print("Starting genut MCP server...")
    print("Available tools:")
    print("  - list_functions: List all functions in a C source file")
    print("  - generate_tests: Generate unit tests for C functions")
    print("  - analyze_function: Analyze a specific function in detail")
    print("\nServer is ready for connections.")

    mcp.run()


if __name__ == "__main__":
    main()
