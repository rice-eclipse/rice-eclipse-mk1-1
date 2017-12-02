//
// Created by rjcunningham on 11/12/17.
//

/**
 * A class that handles the worker thread that interacts with the hardware and generates data.
 * Any multi threaded server must implement this class.
 */

#ifndef SOFTWARE_DATA_WORKER_HPP
#define SOFTWARE_DATA_WORKER_HPP

#include "../server/queue_items.hpp"
#include "../server/safe_queue.hpp"
#include "../server/worker.hpp"
#include "../util/circular_buffer.hpp"

class counter_worker : public worker {
    public:
        circular_buffer &buff;
        counter_worker(safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw,
                           circular_buffer &buff)
                : worker(my_qn, my_qw)
                , buff(buff)
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
 //*/ // How we'd subclass this.
#endif //SOFTWARE_DATA_WORKER_HPP
