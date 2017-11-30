//
// Created by rjcunningham on 11/19/17.
//

#ifndef SOFTWARE_NETWORK_COUNTER_WORKER_HPP_HPP
#define SOFTWARE_NETWORK_COUNTER_WORKER_HPP_HPP

#include "../server/network_worker.hpp"

class network_counter_worker : public network_worker {
    public:
        network_counter_worker(safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw, int port)
        : network_worker(my_qn, my_qw, port)
                {
                };



        bool process_nqi(network_queue_item &nqi);
};

#endif //SOFTWARE_NETWORK_COUNTER_WORKER_HPP_HPP
