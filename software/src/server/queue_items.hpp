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
    wq_none = 0,
    wq_process,
    wq_start,
    wq_stop,
    wq_timed, // Do some timed item with a given datap.
    // Items used for timed items:
    lc_main = 9,
    lc1 = 10,
    lc2 = 11,
    lc3 = 12,
    pt_feed = 13,
    pt_inje = 14,
    pt_comb = 15,
    tc1 = 16,
    tc2 = 17,
    tc3 = 18,
    ign1,
    ign2,
    ign3,
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
    text = 3,
    unset_valve = 4,
    set_valve = 5,
    unset_ignition = 6,
    set_ignition = 7,
    ign_normal = 8,

    // Send codes used for dealing with this stuff.
    lc_mains = 9,
    lc1s = 10,
    lc2s = 11,
    lc3s = 12,
    pt_feeds = 13,
    pt_injes = 14,
    pt_combs = 15,
    tc1s = 16,
    tc2s = 17,
    tc3s = 18
};

struct send_header_t {
    send_code code;
    size_t nbytes;
}; typedef struct send_header_t send_header_t;
#endif //SOFTWARE_QUEUE_ITEMS_HPP
