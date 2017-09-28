cmake_minimum_required(VERSION 2.8.9)
project(software)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES_DUMMY src/main.cpp)
set(SOURCE_FILES_BLINK src/blink/blink.cpp src/blink/blink.cpp)
set(SOURCE_FILES_ECHO_SERVER src/echo_server/listener.cpp src/echo_server/listener.hpp src/echo_server/echo_server.cpp)
set(SOURCE_FILES_SPI_ADC_TEST src/spi/spi.cpp)
add_executable(dummy ${SOURCE_FILES_DUMMY}) #A hello world program.
add_executable(blink ${SOURCE_FILES_BLINK}) #A simple blink file to test stuff.
add_executable(echo_server ${SOURCE_FILES_ECHO_SERVER}) #A simple example echo server for dev later.
add_executable(spi_adc_test ${SOURCE_FILES_SPI_ADC_TEST}) #A simple test to run the adc on a single channel.

add_library(adc_lib.a src/adc/adc_block.cpp) #A static library we can use to run more useful adc code.

target_link_libraries(blink bcm2835)
target_link_libraries(spi_adc_test bcm2835)