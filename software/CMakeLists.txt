cmake_minimum_required(VERSION 2.8.9)
project(software)

set(CMAKE_CXX_STANDARD 11)

set(CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED on)
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")


#LISTS OF SOURCE FILES FOR TARGETS##########################################
set(SOURCE_FILES_DUMMY src/main.cpp)
set(SOURCE_FILES_BLINK src/blink/blink.cpp src/blink/blink.cpp)
set(SOURCE_FILES_SPI_ADC_TEST src/spi/spi.cpp)
set(SOURCE_FILES_ADC_TEST src/adc/adc_test.cpp)
set(SOURCE_FILES_THREADED_ECHO_SERVER src/echo_server/echo_server.cpp
        src/echo_server/listener.cpp src/echo_server/listener.hpp
        src/server/safe_queue.hpp src/server/queue_items.hpp src/util/circular_buffer.cpp src/util/circular_buffer.hpp)
set(SOURCE_FILES_THREADED_ADC_TEST src/adc/threaded_adc_test.cpp
        src/echo_server/listener.cpp src/echo_server/listener.hpp
        src/server/safe_queue.hpp src/server/queue_items.hpp src/util/circular_buffer.cpp src/util/circular_buffer.hpp)
###########################################################################

#LISTS OF BUILD TARGETS####################################################
#A static library we can use to run more useful adc code.
add_library(adc_lib.a src/adc/adc_block.cpp src/adc/adc_test.cpp)
add_executable(adc_test ${SOURCE_FILES_ADC_TEST})
add_executable(blink ${SOURCE_FILES_BLINK}) #A simple blink file to test stuff.
add_executable(dummy ${SOURCE_FILES_DUMMY}) #A hello world program.
add_executable(simple_echo_server src/comm/simple_server.cpp src/echo_server/listener.cpp)
add_executable(simple_send_server src/comm/simple_sender_server.cpp src/echo_server/listener.cpp)
add_executable(spi_adc_test ${SOURCE_FILES_SPI_ADC_TEST}) #A simple test to run the adc on a single channel.
add_executable(threaded_echo_server ${SOURCE_FILES_THREADED_ECHO_SERVER}) #A simple example echo server for dev later.
add_executable(threaded_adc_test ${SOURCE_FILES_THREADED_ADC_TEST}) #A simple example echo server for dev later.
###########################################################################


#DEPENDENCIES##############################################################

add_dependencies(adc_test adc_lib.a)
add_dependencies(threaded_adc_test adc_lib.a)

###########################################################################

#LINKING###################################################################
target_link_libraries(adc_test bcm2835 adc_lib.a)
target_link_libraries(blink bcm2835)
target_link_libraries(spi_adc_test bcm2835)
target_link_libraries(threaded_adc_test bcm2835 adc_lib.a pthread)
target_link_libraries(threaded_echo_server pthread)
###########################################################################