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
#include <poll.h>
#include "../util/circular_buffer.hpp"

class network_worker : public worker {
    public:
        int port;
        int connfd;
        pollfd pf;

        network_worker
                (safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw, int port)
                : worker(my_qn, my_qw)
                , port(port)
        {
        };

        virtual void process_nqi(network_queue_item &nqi) = 0;

        void worker_method();

        void stop() {

        }

};

#endif //SOFTWARE_NETWORK_WORKER_HPP
