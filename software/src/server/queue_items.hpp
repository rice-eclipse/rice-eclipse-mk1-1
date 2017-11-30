//
// Created by rjcunningham on 9/30/17.
//

#ifndef SOFTWARE_QUEUE_ITEMS_HPP
#define SOFTWARE_QUEUE_ITEMS_HPP

#include <cstdint>
#include "../util/circular_buffer.hpp"

enum nqi_type {
    nq_none,
    nq_send,
    nq_recv,
    nq_send_ack,
};

struct network_queue_item {
    nqi_type type;
    circular_buffer *buff;
    size_t nbytes; //The number of bytes to send.
    size_t total_bytes; //The total number of bytes written into the relevant buffer at this point.
    char data[8]; // An extra data field used for simple transactions.
};

enum wqi_type {
    wq_none,
    wq_process,
    wq_start,
    wq_stop
};

struct work_queue_item {
    //FIXME this is a really bad structure if we're actually doing anything with these.
    wqi_type action;
    size_t nbytes; //The size of memory at datap.
    void *extra_datap; //A pointer to the relevant data.
    char data[8]; // An extra data field for simple transactions.
};

enum send_code {
    ack = 1,
    payload = 2, // TODO this payload needs to be something like load cell, etc. etc.
};

struct send_header {
    send_code code;
    size_t nbytes;
};
#endif //SOFTWARE_QUEUE_ITEMS_HPP
