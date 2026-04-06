cmake_minimum_required(VERSION 3.14)
project(TestCProject C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable testing
enable_testing()

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/basic_functions.c
    src/control_flow.c
    src/error_handling.c
    src/stub_dependency.c
    src/memory_management.c
    src/nested_struct_test.c
    src/param_combo.c
)

# Header files (for IDE support)
set(HEADERS
    include/basic_functions.h
    include/control_flow.h
    include/error_handling.h
    include/stub_dependency.h
    include/memory_management.h
    include/nested_struct_test.h
    include/param_combo.h
)

# Create library
add_library(test_c_lib STATIC ${SOURCES} ${HEADERS})

# Create a simple executable for testing (optional)
# add_executable(test_c_project src/main.c)
# target_link_libraries(test_c_project test_c_lib)

# Add math library (only on Unix/Linux)
if(UNIX)
    target_link_libraries(test_c_lib m)
endif()

# --- Google Test Configuration ---
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.tar.gz
)
# For Windows: prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# --- Test Executables ---
# Find all test source files
file(GLOB TEST_SOURCES "test/*.cpp")
file(GLOB TEST_HEADERS "test/*.h")

# Create test executables
foreach(test_source ${TEST_SOURCES})
  get_filename_component(test_name ${test_source} NAME_WE)

  # Skip stub files (they are linked into the matching main test target)
  if(${test_name} MATCHES ".*_stub$")
    continue()
  endif()

  # Include the matching _stub.cpp file if it exists
  set(stub_source "${CMAKE_SOURCE_DIR}/test/${test_name}_stub.cpp")
  if(EXISTS ${stub_source})
    set(test_extra_sources ${stub_source})
  else()
    set(test_extra_sources "")
  endif()

  add_executable(${test_name} ${test_source} ${test_extra_sources} ${TEST_HEADERS})
  target_link_libraries(${test_name} test_c_lib GTest::gtest GTest::gtest_main)
  target_include_directories(${test_name} PRIVATE ${CMAKE_SOURCE_DIR}/include)

  # Add to CTest
  add_test(NAME ${test_name} COMMAND ${test_name})
endforeach()

# Enable compile_commands.json generation
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Installation rules (optional)
# install(TARGETS test_c_project DESTINATION bin)
install(TARGETS test_c_lib DESTINATION lib)
install(FILES ${HEADERS} DESTINATION include)
