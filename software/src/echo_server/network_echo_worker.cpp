//
// Created by rjcunningham on 11/19/17.
//

#include <iostream>
#include <poll.h>
#include "network_echo_worker.hpp"
#include "../util/listener.hpp"

bool network_echo_worker::process_nqi(network_queue_item &nqi) {
    char c;
    work_queue_item wqi;
    ssize_t read_result;

    switch (nqi.type) {
        case (nq_recv): {
            read_result = do_recv(connfd, &c, 1);
            if (read_result <= 0) {
                //FIXME, do something better?
                return true;
            }

            wqi.action = wq_process;
            wqi.data[0] = c;
            qw.enqueue(wqi);
            return true;

        }
        case (nq_send): {
            //Poll before we read:
            if (poll(&pf, 1, 0) == 0) {
                if (!pf.revents & POLLOUT) {
                    //Cannot write. Will block.
                    std::cerr << "Socket blocked" << std::endl;
                    return false; //TODO this is an error that isn't what we wanted.
                }
            }
            c = nqi.data[0];
            network_worker::send_header(text, 1);
            write(connfd, &c, 1);
            return true;

        }
        default: {
            return network_worker::process_nqi(nqi);
        }
    }
}