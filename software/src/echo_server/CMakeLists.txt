project(echo_server)

set(SOURCE_FILES echo_worker.cpp ../server/network_worker.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})

add_dependencies(${PROJECT_NAME} circ_buff.a listener.a)

target_link_libraries(${PROJECT_NAME} circ_buff.a listener.a pthread)