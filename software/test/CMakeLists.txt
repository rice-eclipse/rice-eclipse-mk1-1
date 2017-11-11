#Subdirectory for testing:
add_library(libtest.a catch_main.cpp)
enable_testing()

macro(add_catch_test name)
    add_test(NAME ${name} COMMAND ${name})
endmacro()

add_subdirectory(circular_buffer)
add_subdirectory(threaded_circular_buffer)