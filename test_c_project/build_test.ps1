#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"
$SCRIPT_DIR = Split-Path $MyInvocation.MyCommand.Path -Parent
$BUILD_DIR = Join-Path $SCRIPT_DIR "build_tests"

# 可通过环境变量覆盖编译器路径
$CXX_COMPILER = if ($env:CXX) { $env:CXX } else { "D:/Program Files/LLVM/bin/clang++.exe" }

if ($args[0] -eq "clean") {
    Write-Host "=== Cleaning test build directory ===" -ForegroundColor Green
    if (Test-Path $BUILD_DIR) {
        Remove-Item -Recurse -Force $BUILD_DIR
    }
    Write-Host "Done."
    exit 0
}

Write-Host "=== Configuring tests ===" -ForegroundColor Green
cmake -S (Join-Path $SCRIPT_DIR "test") `
      -B $BUILD_DIR `
      -G "MinGW Makefiles" `
      -DCMAKE_CXX_COMPILER="$CXX_COMPILER"

if ($LASTEXITCODE -ne 0) {
    Write-Host "CMake configuration failed" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "=== Building tests ===" -ForegroundColor Green
cmake --build $BUILD_DIR --target tests

if ($LASTEXITCODE -ne 0) {
    Write-Host "CMake build failed" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "=== Running tests ===" -ForegroundColor Green
Push-Location $BUILD_DIR
try {
    ctest --output-on-failure
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Some tests failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}

Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "  Test build directory:  $BUILD_DIR"
Write-Host "  To run specific test:  .\test_basic_functions.exe"