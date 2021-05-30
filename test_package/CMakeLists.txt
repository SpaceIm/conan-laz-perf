cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(lazperf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET LAZPERF::lazperf)
    target_link_libraries(${PROJECT_NAME} LAZPERF::lazperf)
else()
    target_link_libraries(${PROJECT_NAME} LAZPERF::lazperf_s)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
