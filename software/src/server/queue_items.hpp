//
// Created by rjcunningham on 9/30/17.
//

#ifndef SOFTWARE_QUEUE_ITEMS_HPP
#define SOFTWARE_QUEUE_ITEMS_HPP

#include <cstdint>
using namespace std;

enum nqi_type {
    nq_send,
    nq_recv
};

struct network_queue_item {
    nqi_type type;
    uint8_t data;
};

enum wqi_type {
    wq_process
};

struct work_queue_item {
    wqi_type action;
    uint8_t data;
};

#endif //SOFTWARE_QUEUE_ITEMS_HPP
