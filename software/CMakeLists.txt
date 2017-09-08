cmake_minimum_required(VERSION 2.8.9)
project(software)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES_DUMMY src/main.cpp)
set(SOURCE_FILES_BLINK src/blink/blink.cpp src/blink/blink.cpp)
set(SOURCE_FILES_ECHO_SERVER src/echo_server/listener.cpp src/echo_server/listener.hpp src/echo_server/echo_server.cpp)
add_executable(dummy ${SOURCE_FILES_DUMMY})
add_executable(blink ${SOURCE_FILES_BLINK})
add_executable(echo_server ${SOURCE_FILES_ECHO_SERVER})
target_link_libraries(blink bcm2835)
