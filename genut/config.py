"""Configuration classes for UT generation."""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NamingConfig:
    """Naming convention configuration for generated test files."""
    file_prefix: str = "ut_"  # Output file prefix
    file_suffix: str = ""     # Output file suffix
    suite_suffix: str = "Test"  # Test suite suffix
    test_name_pattern: str = "{func}_Path{index}"  # Test case naming pattern


@dataclass
class DefaultValueConfig:
    """Default value configuration for different types."""
    int_default: str = "0"
    float_default: str = "0.0"
    pointer_default: str = "NULL"
    struct_default: str = "{}"
    bool_default: str = "0"
    # Support custom type mappings
    custom_type_defaults: Dict[str, str] = field(default_factory=dict)


@dataclass
class GeneratorConfig:
    """Main configuration class for UT generation."""
    naming: NamingConfig = field(default_factory=NamingConfig)
    default_values: DefaultValueConfig = field(default_factory=DefaultValueConfig)
    basic_type_keywords: List[str] = field(default_factory=lambda: [
        'int', 'char', 'float', 'double', 'long', 'short',
        'bool', 'size_t', 'unsigned', 'signed'
    ])
    compiler: str = "auto"  # "auto", "gcc", "clang"
    copyright_header: List[str] = field(default_factory=list)  # Lines to add as copyright header
    extra_includes: List[str] = field(default_factory=list)  # Additional headers to include

    @classmethod
    def from_file(cls, config_path: str) -> 'GeneratorConfig':
        """Load configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        naming_data = data.get('naming', {})
        naming = NamingConfig(**naming_data) if naming_data else NamingConfig()

        defaults_data = data.get('default_values', {})
        defaults = DefaultValueConfig(**defaults_data) if defaults_data else DefaultValueConfig()

        return cls(
            naming=naming,
            default_values=defaults,
            basic_type_keywords=data.get('basic_type_keywords', cls.__dataclass_fields__['basic_type_keywords'].default_factory()),
            compiler=data.get('compiler', 'auto'),
            copyright_header=data.get('copyright_header', []),
            extra_includes=data.get('extra_includes', [])
        )

    @classmethod
    def default(cls) -> 'GeneratorConfig':
        """Create default configuration."""
        return cls()