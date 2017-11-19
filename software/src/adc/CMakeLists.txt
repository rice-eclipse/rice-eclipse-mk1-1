add_subdirectory(lib)

set(SOURCE_FILES_ADC_TEST adc_test.cpp)
add_executable(adc_test ${SOURCE_FILES_ADC_TEST})
add_dependencies(adc_test adc_lib.a)
target_link_libraries(adc_test bcm2835 adc_lib.a)