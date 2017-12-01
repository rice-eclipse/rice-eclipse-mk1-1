//
// Created by rjcunningham on 11/18/17.
//
#include <iostream>
#include <poll.h>
#include "network_counter_worker.hpp"
#include "../util/listener.hpp"

bool network_counter_worker::process_nqi(network_queue_item &nqi) {
    char c;
    work_queue_item wqi;
    ssize_t read_result;

    switch (nqi.type) {
        case (nq_recv): {
            //Poll before we read:
            read_result = do_recv(connfd, &c, 1);
            if (read_result <= 0) {
                //FIXME, do something better?
                return true;
            }
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
                    return true;
                }
            }
            circular_buffer &buff = *nqi.buff;

            network_worker::send_header(payload, nqi.nbytes);

            std::cout << "Writing data" << std::endl;
            if (buff.write_data(connfd, nqi.nbytes, nqi.total_bytes) != 0) {
                std::cerr << "Connection Closed" << std::endl;
                //exit(0);
            }

            break;

        }
        default: {
            return network_worker::process_nqi(nqi);
        }
    }

    return true;
}

