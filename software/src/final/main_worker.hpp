//
// Created by rjcunningham on 12/1/17.
//

#ifndef SOFTWARE_MAIN_WORKER_HPP
#define SOFTWARE_MAIN_WORKER_HPP

#include "../util/circular_buffer.hpp"
#include "../server/worker.hpp"
#include "../adc/lib/adc_block.hpp"
#include "../util/timestamps.hpp"
#include "main_network_worker.hpp"

struct adc_reading {
    uint16_t dat;
    uint64_t t;
};
extern struct adc_reading adcd;

class main_worker : public worker {
    public:
        circular_buffer &buff;
        adc_block &adcs;
        main_network_worker *nw_ref;
        main_worker(safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw,
                       circular_buffer &buff, adc_block &adcs, main_network_worker *nw_ref)
                : worker(my_qn, my_qw)
                , buff(buff)
                , adcs(adcs)
                , nw_ref(nw_ref)
        {
        };

        void start()
        {
            worker::start();
        }

        void worker_method();

        void stop() {
        }


};

#define CIRC_SIZE 1 << 16

extern network_queue_item null_nqi; //An item for null args to
extern work_queue_item null_wqi; //An object with the non-matching type to do nothing.

// TODO please put these times somewhere less stupid.
// Times used for setting timed actions.
#define LC_MAIN_T 500

#define LC1_T 1000
#define LC2_T LC1_T
#define LC3_T LC1_T

#define PT_FEED_T 1000
#define PT_INJE_T PT_FEED_T
#define PT_COMB_T PT_FEED_T

#define TC1_T 20000
#define TC2_T TC1_T
#define TC3_T TC1_T

#define IGN2_T 250000 //250ms
#define IGN3_T 3000000 // 3000 ms

#define MAX_TIMED_LIST_LEN 20

struct timed_item {
    timestamp_t scheduled;
    timestamp_t delay;
    circular_buffer *b; // The output buffer used by this item.
    adc_info ai; // The adc info used to call the sampler:
    wqi_type a;
    bool enabled;
    timestamp_t last_send; // A dumb value used to track when it was last sent.
    size_t nbytes_last_send;
}; typedef struct timed_item timed_item;

#endif //SOFTWARE_MAIN_WORKER_HPP
