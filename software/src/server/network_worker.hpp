//
// Created by rjcunningham on 11/12/17.
//

/**
 * A class that handles the worker thread that interacts with the network.
 * Any multi threaded server must implement this class.
 */

#ifndef SOFTWARE_NETWORK_WORKER_HPP
#define SOFTWARE_NETWORK_WORKER_HPP

#include "queue_items.hpp"
#include "safe_queue.hpp"
#include "worker.hpp"
#include "../util/circular_buffer.hpp"

class network_worker : public worker {
    public:
        circular_buffer &buff;
        int port;
        network_worker
                (safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw, int port,
                 circular_buffer &buff)
                : worker(my_qn, my_qw)
                , port(port)
                , buff(buff)

        {
        };

        void worker_method();

        void stop() {

        }

};

#endif //SOFTWARE_NETWORK_WORKER_HPP
