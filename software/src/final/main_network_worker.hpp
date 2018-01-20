//
// Created by rjcunningham on 11/29/17.
//

#ifndef SOFTWARE_MAIN_NETWORK_WORKER_HPP
#define SOFTWARE_MAIN_NETWORK_WORKER_HPP


#include "../server/network_worker.hpp"

class main_network_worker : public network_worker {
    public:
        circular_buffer &buff;
        main_network_worker(safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw, int port,
        circular_buffer &buff)
        : network_worker(my_qn, my_qw, port)
        , buff(buff)
        {
        };

        bool process_nqi(network_queue_item &nqi);
};


#endif //SOFTWARE_MAIN_NETWORK_WORKER_HPP
