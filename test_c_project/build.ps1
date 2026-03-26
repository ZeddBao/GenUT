$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildDir = Join-Path $ScriptDir "build"

$CCompiler = if ($env:CC) { $env:CC } else { "D:\Program Files\LLVM\bin\clang.exe" }
$CCompiler = $CCompiler.Replace("\", "/")

if ($args[0] -eq "clean") {
    Write-Host "=== Cleaning build directory ==="
    if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }
    $JsonFile = Join-Path $ScriptDir "compile_commands.json"
    if (Test-Path $JsonFile) { Remove-Item -Force $JsonFile }
    Write-Host "Done."
    exit 0
}

Write-Host "=== Configuring ==="
cmake -S $ScriptDir `
      -B $BuildDir `
      -G "MinGW Makefiles" `
      -DCMAKE_C_COMPILER="$CCompiler" `
      -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

Write-Host "=== Building ==="
cmake --build $BuildDir

Write-Host "=== Copying compile_commands.json to project root ==="
(Get-Content "$BuildDir\compile_commands.json" -Raw) -replace '\\\\', '/' |
    Set-Content "$ScriptDir\compile_commands.json" -NoNewline

Write-Host "=== Done ==="
Write-Host "  Binary:            $BuildDir\test_c_project.exe"
Write-Host "  compile_commands:  $ScriptDir\compile_commands.json"
