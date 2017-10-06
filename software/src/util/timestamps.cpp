//
// Created by rjcunningham on 10/6/17.
//

#include "timestamps.hpp"
timestamp_t get_time() {
    //We could just return tv, but whatever.
    struct timeval tv;
    gettimeofday(&tv, nullptr); //Use a magic unix syscall.

    //Cast value to make value into 64 bit.
    return ((uint64_t) tv.tv_sec) * 1000000 + tv.tv_usec;
}