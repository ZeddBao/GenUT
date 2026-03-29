#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build_tests"

# 可通过环境变量覆盖编译器路径
CXX_COMPILER="${CXX:-D:/Program Files/LLVM/bin/clang++.exe}"

if [[ "$1" == "clean" ]]; then
    echo "=== Cleaning test build directory ==="
    rm -rf "$BUILD_DIR"
    echo "Done."
    exit 0
fi

echo "=== Configuring tests ==="
cmake -S "$SCRIPT_DIR/test" \
      -B "$BUILD_DIR" \
      -G "MinGW Makefiles" \
      -DCMAKE_CXX_COMPILER="$CXX_COMPILER"

echo "=== Building tests ==="
cmake --build "$BUILD_DIR" --target tests

echo "=== Running tests ==="
cd "$BUILD_DIR"
ctest --output-on-failure

echo "=== Done ==="
echo "  Test build directory:  $BUILD_DIR"
echo "  To run specific test:  ./test_basic_functions.exe"