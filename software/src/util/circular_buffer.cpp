//
// Created by rjcunningham on 10/4/17.
//

#include "unistd.h"
#include <cstring>
#include <iostream>
#include "circular_buffer.hpp"

#define DEBUG_CIRC_SEND

circular_buffer::circular_buffer(size_t size) : bytes_written(0) {
    this->nbytes = size;
    this->data = new char[size];
}

circular_buffer::~circular_buffer() {
    delete [] this->data;
}

void circular_buffer::add_data(void *p, size_t n) {
    size_t bw = bytes_written.load();
    size_t to_add = nbytes - bw % this->nbytes; // The distance between start and the end of the buffer.
    to_add = to_add > n ? n : to_add; //Take the minimum value of n and to_add.
    memcpy(this->data + bw % this->nbytes, p, to_add);
    n -= to_add;
    bytes_written += to_add;
    if (n != 0)
        this->add_data((char *)p + to_add, n);
}

ssize_t circular_buffer::write_data(int fd, size_t n, size_t offset) {
    if (offset < bytes_written.load() - this->nbytes) {
        std::cerr << "Bytes already overwritten before sending" << std::endl;
        return -1; //TODO don't collide with write error?
    }
    size_t to_send = nbytes - offset % this->nbytes; // The distance between start and the end of the buffer.
    to_send = to_send > n ? n : to_send; //Take the minimum value of n and to_send.
    ssize_t result;
    result = write(fd, data + offset % this->nbytes, to_send);
    if (result <= 0) {
        return result;
    } else {
        //Need to send slightly less data now:
        return write_data(fd, n - result, offset + result);
    }
}

void circular_buffer::zero() {
    bzero(data, nbytes);
    bytes_written = 0;
}
