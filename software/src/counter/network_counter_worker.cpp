//
// Created by rjcunningham on 11/18/17.
//
#include <iostream>
#include <poll.h>
#include "network_counter_worker.hpp"
#include "../util/listener.hpp"

void network_counter_worker::process_nqi(network_queue_item &nqi) {
    char c;
    work_queue_item wqi;
    ssize_t read_result;

    switch (nqi.type) {
        case (nq_recv): {
            //Poll before we read:
            if (poll(&pf, 1, 0) >= 0) {
                if (!(pf.revents & POLLIN)) {
                    // Nothing to read.
                    //std::cerr << "Socket blocked on read" << std::endl;
                    //Go back to looping.
                    break;
                }
            } else {
                std::cerr << "Poll failed" << std::endl;
                exit(1);
            }
            read_result = read(connfd, &c, 1);
            /*
             * If we get a '0' then start processing stuff.
             * If we get a '1' then stop processing stuff.
             * Otherwise ignore the message.
             */
            if (c == '0') {
                wqi.action = wq_start;
            } else if (c == '1') {
                wqi.action = wq_stop;
            } else {
                wqi.action = wq_none;
            }
            qw.enqueue(wqi);
            break;
        }
        case (nq_send): {
            //Poll before we read:
            if (poll(&pf, 1, 0) == 0) {
                if (!pf.revents & POLLOUT) {
                    //Cannot write. Will block.
                    std::cerr << "Socket blocked" << std::endl;
                    return;
                }
            }
            circular_buffer &buff = *nqi.buff;
            std::cout << "Writing data" << std::endl;
            if (buff.write_data(connfd, nqi.nbytes, nqi.total_bytes) != 0) {
                std::cerr << "Connection Closed" << std::endl;
                //exit(0);
            }

            break;

        }
        case (nq_none): {
            nqi.type = nq_recv;
            qn.enqueue(nqi); //Just always be reading because otherwise we're screwed.
            // FIXME need to do some checking to make sure this happens frequently.
        }
    }
}