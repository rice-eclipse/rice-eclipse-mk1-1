//
// Created by rjcunningham on 12/1/17.
//

#ifndef SOFTWARE_MAIN_WORKER_HPP
#define SOFTWARE_MAIN_WORKER_HPP

#include "../util/circular_buffer.hpp"
#include "../server/worker.hpp"
#include "../adc/lib/adc_block.hpp"

struct adc_reading {
    uint16_t dat;
    uint64_t t;
};
extern struct adc_reading adcd;

class main_worker : public worker {
    public:
        circular_buffer &buff;
        adc_block &adcs;
        main_worker(safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw,
                       circular_buffer &buff, adc_block &adcs)
                : worker(my_qn, my_qw)
                , buff(buff)
                , adcs(adcs)
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

#endif //SOFTWARE_MAIN_WORKER_HPP
