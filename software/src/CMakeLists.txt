add_subdirectory(util) # Build all utility libraries first.
add_subdirectory(echo_server) # Build the echo server test thingy.
add_subdirectory(counter)
add_subdirectory(adc) # ADC code has minimal dependencies.
add_subdirectory(final)