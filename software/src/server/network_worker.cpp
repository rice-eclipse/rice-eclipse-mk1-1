//
// Created by rjcunningham on 11/18/17.
//
#include <iostream>
#include <poll.h>
#include "network_worker.hpp"
#include "../util/listener.hpp"
#include "../util/timestamps.hpp"

void network_worker::worker_method() {
    ssize_t read_result;
    char c;
    network_queue_item nqi;
    work_queue_item wqi;

    pf.events = POLLIN | POLLOUT;

    while (1) {
        //std::cout << "Networker entering loop:\n";
        nqi = qn.poll();
        //std::cout << "Networker got item:\n";

        if (!process_nqi(nqi)) {
            std::cerr << "Could not process request on network thread: " << nqi.type << std::endl;
        }
    }
}

bool network_worker::process_nqi(network_queue_item &nqi) {
    if (!connected) {
        std::cout << "Attempting to connect" << std::endl;
        open_connection();
    }
    switch (nqi.type) {
        case (nq_none): {


            timestamp_t t = get_time();
            // First check if we are close to timing out:
            if (timeout > 0 && t - last_recv > timeout) {
                std::cerr << "Connection timed out." << std::endl;
                fail_connection();
                return true;
            } else if (timeout > 0 && !has_acked && t - last_recv > timeout / 2) {
                //TODO maybe add this as debug option.
                std::cerr << "Connection inactive. Sending ack." << std::endl;
                nqi.type = nq_send_ack;
                qn.enqueue(nqi);
                return true;
            }

            //TODO is this messing with an object we don't own? Doesn't seem to be.
            nqi.type = nq_recv;
            qn.enqueue(nqi); //Just always be reading because otherwise we're screwed.
            // FIXME need to do some checking to make sure this happens frequently.
            return true;
        }
        default: {
            return false;
        }
    }
}

ssize_t network_worker::do_recv(int fd, char *b, size_t nbytes) {
    ssize_t read_result;

    //Poll before we read:
    if (poll(&pf, 1, 0) >= 0) {
        if (!(pf.revents & POLLIN)) {
            // Nothing to read.
            //std::cerr << "Socket blocked on read" << std::endl;
            //Go back to looping.
            return -2;
        }
    } else {
        std::cerr << "Poll failed" << std::endl;
        exit(1);
    }
    read_result = read(fd, b, nbytes);
    if (read_result > 0) {
        /*
         * Update our timing on when we last received.
         */
        timestamp_t trecv = get_time();
        this->last_recv = trecv;
        this->has_acked = false; // No longer need to ack, so ignore these.
    } else if (read_result == 0) {
        /*
         * Check if the file descriptor has closed:
         */
        std::cerr << "Read nothing from socket. Assuming it is dead." << std::endl;
        fail_connection();
    }

    return read_result;
}

void network_worker::fail_connection() {
    close(connfd);
    connfd = -1;
    pf.fd = -1;

    connected = false;
}

void network_worker::open_connection() {
    connfd = wait_for_connection(port, NULL);
    if (connfd < 0)
        std::cerr << "Could not open connection fd." << std::endl;

    /*
     * Stuff used to poll the socket:
     */
    pf.fd = connfd;

    /*
     * Update the last received and mark that we are connected:
     */
    connected = true;
    has_acked = false;
    last_recv = get_time();
}