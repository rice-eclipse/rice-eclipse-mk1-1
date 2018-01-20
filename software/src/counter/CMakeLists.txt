project(counter)

set(SOURCE_FILES counter_worker.cpp ../server/network_worker.cpp network_counter_worker.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})

add_dependencies(${PROJECT_NAME} circ_buff.a listener.a timestamps.a)

target_link_libraries(${PROJECT_NAME} circ_buff.a listener.a pthread timestamps.a)