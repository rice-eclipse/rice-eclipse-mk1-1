//
// Created by rjcunningham on 10/6/17.
//

#ifndef SOFTWARE_TIMESTAMPS_HPP
#define SOFTWARE_TIMESTAMPS_HPP

#include <cstdint>
#include <sys/time.h>

/*
 * A way to generate microsecond timestamps for stuff.
 */
typedef uint64_t timestamp_t;

void set_base_time();

timestamp_t get_time();

#endif //SOFTWARE_TIMESTAMPS_HPP
