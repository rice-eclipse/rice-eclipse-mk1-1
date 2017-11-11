set(SOURCE_FILES_THREADED_CIRCULAR_BUFFER_TEST threaded_circular_buffer_test.cpp
        ../../src/echo_server/listener.cpp ../../src/server/safe_queue.hpp)

add_executable(threaded_circular_buffer_test ${SOURCE_FILES_THREADED_CIRCULAR_BUFFER_TEST})
#A simple example echo server for dev later.

add_dependencies(threaded_circular_buffer_test circ_buff.a timestamps.a)

target_link_libraries(threaded_circular_buffer_test bcm2835 pthread circ_buff.a timestamps.a)