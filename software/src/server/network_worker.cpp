//
// Created by rjcunningham on 11/18/17.
//
#include <iostream>
#include <poll.h>
#include "network_worker.hpp"
#include "../util/listener.hpp"

void network_worker::worker_method() {
    ssize_t read_result;
    char c;
    network_queue_item nqi;
    work_queue_item wqi;


    connfd = wait_for_connection(port, NULL);
    if (connfd < 0)
        std::cerr << "Could not open connection fd." << std::endl;

    /*
     * Stuff used to poll the socket:
     */
    pf.fd = connfd;
    pf.events = POLLIN | POLLOUT;

    while (1) {
        //std::cout << "Networker entering loop:\n";
        nqi = qn.poll();
        //std::cout << "Networker got item:\n";

        process_nqi(nqi);

    }
}
