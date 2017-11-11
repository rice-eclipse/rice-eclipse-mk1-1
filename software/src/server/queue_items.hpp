//
// Created by rjcunningham on 9/30/17.
//

#ifndef SOFTWARE_QUEUE_ITEMS_HPP
#define SOFTWARE_QUEUE_ITEMS_HPP

#include <cstdint>
using namespace std;

enum nqi_type {
    nq_none,
    nq_send,
    nq_recv
};

struct network_queue_item {
    nqi_type type;
    size_t nbytes; //The number of bytes to send.
    size_t total_bytes; //The total number of bytes written into the relevant buffer at this point.
};

enum wqi_type {
    wq_none,
    wq_process,
    wq_start,
    wq_stop
};

struct work_queue_item {
    wqi_type action;
    size_t nbytes; //The size of memory at nbytes.
    void *datap; //A pointer to the relevant data.
};

#endif //SOFTWARE_QUEUE_ITEMS_HPP
