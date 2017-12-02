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
#include "../util/timestamps.hpp"

class network_worker : public worker {
    public:
        int port;
        int connfd;
        bool connected;

        /**
         * The number of microseconds where no receive has occured before the worker should treat the peer
         * as disconnected. If timeout equals zero, then the worker will not attempt to track timeouts or
         * request acks from the base station.
         */
        timestamp_t timeout;

        /**
         * The time in microseconds when we last received our connection.
         */
        std::atomic<uint64_t> last_recv;

        network_worker
                (safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw, int port)
                : network_worker(my_qn, my_qw, port, 0){};

        network_worker
                (safe_queue<network_queue_item> &my_qn, safe_queue<work_queue_item> &my_qw, int port,
                 timestamp_t timeout)
                : worker(my_qn, my_qw)
                , port(port)
                , last_recv(0)
                , timeout(timeout)
                , connfd(-1)
        {
                last_recv = get_time() - timeout; // Set the last time such that we are immediately timed out.
        };

        /**
         * The method used to process a new request for this worker.
         * @param nqi The network queue item to process.
         * @return Returns true if the network item was processed and false if not.
         */
        virtual bool process_nqi(network_queue_item &nqi);

        void worker_method();

        void stop() {

        }

        /**
         * Destroys the open connection and returns the network worker to a state of waiting for a connection.
         */
        void fail_connection();

        /**
         * Opens the listener and waits for a new connection. Usually after a
         */
        void open_connection();


        ssize_t send_header(send_code h, size_t nbytes);

        ssize_t rwrite(int fd, void *b, size_t n);

    protected:
        /**
         * A simple wrapper over read that handles errors and updates the timeout information.
         * @param fd
         * @param b
         * @param nbytes
         * @return Whatever read returned. -2 if poll succeeded but there was nothing to receive. -3 if poll failed.
         */
        ssize_t do_recv(int fd, char *b, size_t nbytes);
        pollfd pf;

        bool has_acked;
};


#endif //SOFTWARE_NETWORK_WORKER_HPP
