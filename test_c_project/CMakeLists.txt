cmake_minimum_required(VERSION 3.10)
project(TestCProject C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/math_utils.c
    src/data_processor.c
    src/state_machine.c
    src/sensor.c
    src/global_ptr_test.c
    src/stub_test.c
)

# Header files (for IDE support)
set(HEADERS
    include/math_utils.h
    include/data_processor.h
    include/state_machine.h
    include/sensor.h
    include/global_ptr_test.h
    include/stub_test.h
)

# Create library
add_library(test_c_lib STATIC ${SOURCES} ${HEADERS})

# Create executable
add_executable(test_c_project src/main.c)
target_link_libraries(test_c_project test_c_lib)

# Add math library (only on Unix/Linux)
if(UNIX)
    target_link_libraries(test_c_project m)
endif()

# Enable compile_commands.json generation
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Installation rules
install(TARGETS test_c_project DESTINATION bin)
install(FILES ${HEADERS} DESTINATION include)
