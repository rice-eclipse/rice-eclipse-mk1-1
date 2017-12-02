project(final)

add_executable(${PROJECT_NAME} main.cpp initialization.cpp initialization.hpp main_network_worker.cpp main_network_worker.hpp
        ../server/network_worker.cpp ../server/network_worker.hpp ../server/worker.hpp pins.hpp main_worker.cpp main_worker.hpp pins.cpp)

SET(FINAL_LIBS timestamps.a listener.a circ_buff.a adc_lib.a)

SET(FINAL_LIBS_EXT bcm2835 pthread)

add_dependencies(${PROJECT_NAME} ${FINAL_LIBS})



target_link_libraries(${PROJECT_NAME} ${FINAL_LIBS} ${FINAL_LIBS_EXT})