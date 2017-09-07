cmake_minimum_required(VERSION 2.8.9)
project(software)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES_DUMMY src/main.cpp)
set(SOURCE_FILES_BLINK src/blink/blink.cpp src/blink/blink.cpp)
add_executable(dummy ${SOURCE_FILES_DUMMY})
add_executable(blink ${SOURCE_FILES_BLINK})
target_link_libraries(blink bcm2835)
