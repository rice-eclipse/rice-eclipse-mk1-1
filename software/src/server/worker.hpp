//
// Created by rjcunningham on 11/18/17.
//

#ifndef SOFTWARE_WORKER_HPP
#define SOFTWARE_WORKER_HPP

#include <thread>
#include "queue_items.hpp"
#include "safe_queue.hpp"

/**
 * A simple abstraction over a new worker thread that can read and write to work queues
 * on the network.
 */
class worker {

    public:
        safe_queue<network_queue_item> &qn;
        safe_queue<work_queue_item> &qw;

        /**
         * Create a new worker.
         * @param my_qn The network queue to use.
         * @param my_qw The (data) work queue to use.
         */
        worker(safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw)
                : qn(my_qn)
                , qw(my_qw)
        {

        };


        /**
         * This method is forked into a new thread when start is called.
         * Should be used to read and write from the queues and either interact
         * with the hardware or with the networking.
         */
        virtual void worker_method() = 0;

        /**
         * Starts the data worker's threads.
         */
        virtual void start() {
            t_main = std::thread(&worker::worker_method, this);
        };

        /**
         * Stops the data worker's processing and flushes logs to disk.
         * TODO register this as a function called on exit.
         */
        virtual void stop() = 0;

        /**
         * Blocks until the stop method on the data_worker has been called.
         */
        virtual void wait() {
            t_main.join();
        };

    private:
        /**
         * The single main thread for the worker. By default a single thread is assumed.
         */
        std::thread t_main;


};

#endif //SOFTWARE_WORKER_HPP
