//
// Created by rjcunningham on 11/29/17.
//


#include <iostream>
#include "main_network_worker.hpp"
bool main_network_worker::process_nqi(network_queue_item &nqi) {
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
            //TODO just make this a process and let the logic in the worker handle it.
            /*
             * If we get a '0' then start processing stuff.
             * If we get a '1' then stop processing stuff.
             * Otherwise ignore the message.
             */
            wqi.action = wq_process;
            wqi.data[0] = c;
            qw.enqueue(wqi);
            return true;
        }
        case (nq_send_ack): {
            // Don't actually send an ack. Just don't timeout for now.
            //network_worker::send_header(ack, 0);
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

            // TODO this header should correspond to something from the nqi data.
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
}
