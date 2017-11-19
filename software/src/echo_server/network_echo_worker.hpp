//
// Created by rjcunningham on 11/19/17.
//

#ifndef SOFTWARE_NETWORK_ECHO_WORKER_HPP
#define SOFTWARE_NETWORK_ECHO_WORKER_HPP


#include "../server/network_worker.hpp"

class network_echo_worker : public network_worker{
    public:
        network_echo_worker(safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw, int port)
        : network_worker(my_qn, my_qw, port)
        {
        };

        void process_nqi(network_queue_item &nqi);

};


#endif //SOFTWARE_NETWORK_ECHO_WORKER_HPP
