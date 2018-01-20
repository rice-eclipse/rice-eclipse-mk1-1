project(echo_server)

set(SOURCE_FILES echo_worker.cpp ../server/network_worker.cpp network_echo_worker.cpp network_echo_worker.hpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})

add_dependencies(${PROJECT_NAME} circ_buff.a listener.a timestamps.a)

target_link_libraries(${PROJECT_NAME} circ_buff.a listener.a pthread timestamps.a)