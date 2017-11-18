#test the circular buffer
project(circular_buffer_test)

add_executable(${PROJECT_NAME} ${PROJECT_NAME}.cpp)

add_dependencies(${PROJECT_NAME} circ_buff.a libtest.a)

target_link_libraries(${PROJECT_NAME} circ_buff.a libtest.a)

add_catch_test(${PROJECT_NAME})
