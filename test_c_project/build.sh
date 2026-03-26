#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"

# 可通过环境变量覆盖编译器路径
C_COMPILER="${CC:-D:/Program Files/LLVM/bin/clang.exe}"

if [[ "$1" == "clean" ]]; then
    echo "=== Cleaning build directory ==="
    rm -rf "$BUILD_DIR"
    rm -f "$SCRIPT_DIR/compile_commands.json"
    echo "Done."
    exit 0
fi

echo "=== Configuring ==="
cmake -S "$SCRIPT_DIR" \
      -B "$BUILD_DIR" \
      -G "MinGW Makefiles" \
      -DCMAKE_C_COMPILER="$C_COMPILER" \
      -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

echo "=== Building ==="
cmake --build "$BUILD_DIR"

echo "=== Copying compile_commands.json to project root ==="
sed 's/\\\\/\//g' "$BUILD_DIR/compile_commands.json" > "$SCRIPT_DIR/compile_commands.json"

echo "=== Done ==="
echo "  Binary:            $BUILD_DIR/test_c_project.exe"
echo "  compile_commands:  $SCRIPT_DIR/compile_commands.json"
