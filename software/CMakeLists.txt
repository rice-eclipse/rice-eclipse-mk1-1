cmake_minimum_required(VERSION 2.8.9)
project(software)

set(CMAKE_CXX_STANDARD 11)

set(CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED on)
if(BUILD_RPI)
    SET(CMAKE_CXX_COMPILER g++)
endif()
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES_DUMMY src/echo_server/echo_worker.hpp src/server/network_worker.hpp src/server/worker.hpp
        src/server/network_worker.cpp src/echo_server/echo_worker.cpp)
add_custom_target(dummy SOURCES ${SOURCE_FILES_DUMMY})

#SUBDIRECTORIES#############################################################
add_subdirectory(test)
add_subdirectory(src)
############################################################################

#LISTS OF SOURCE FILES FOR TARGETS##########################################
set(SOURCE_FILES_SPI_ADC_TEST src/spi/spi.cpp)
set(SOURCE_FILES_THREADED_ECHO_SERVER src/counter/threaded_counter.cpp
        src/server/safe_queue.hpp src/server/queue_items.hpp)
set(SOURCE_FILES_THREADED_ADC_TEST src/adc/threaded_adc_test.cpp
        src/server/safe_queue.hpp src/server/queue_items.hpp)
###########################################################################

#LISTS OF BUILD TARGETS####################################################
add_executable(spi_adc_test ${SOURCE_FILES_SPI_ADC_TEST}) #A simple test to run the adc on a single channel.
add_executable(threaded_echo_server ${SOURCE_FILES_THREADED_ECHO_SERVER}) #A simple example echo server for dev later.
add_executable(threaded_adc_test ${SOURCE_FILES_THREADED_ADC_TEST}) #A simple example echo server for dev later.
###########################################################################


#DEPENDENCIES##############################################################
add_dependencies(threaded_adc_test adc_lib.a circ_buff.a timestamps.a listener.a)
add_dependencies(threaded_echo_server listener.a)
add_dependencies(spi_adc_test adc_lib.a)

###########################################################################

#LINKING###################################################################
target_link_libraries(spi_adc_test bcm2835)
target_link_libraries(threaded_adc_test bcm2835 adc_lib.a pthread circ_buff.a timestamps.a listener.a)
target_link_libraries(threaded_echo_server pthread circ_buff.a listener.a)
###########################################################################
