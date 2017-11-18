//
// Created by rjcunningham on 11/18/17.
//

#include <zconf.h>
#include <iostream>
#include "echo_worker.hpp"
#include "../server/network_worker.hpp"

void echo_worker::worker_method() {
    network_queue_item nqi;
    work_queue_item wqi;
    char c;
    bool sending = false;
    size_t last_send = 0;
    uint16_t count = 0;

    while (1) {
        //std::cout << "Backworker entering loop:\n";
        wqi = qw.poll();
        //std::cout << "Backworker got item:\n";
        switch (wqi.action) {
            case (wq_process): {
                //For now we're not handling this.
                /*
                c = wqi.data;
                //Make the character lowercase.
                if (c <= 'Z' && c >= 'A') {
                    c -= ('A' - 'a');
                }

                std::cout << c; //Write the byte.

                //Send c back over the socket.
                nqi.type = nq_send;
                nqi.data = (uint8_t) c;
                qn.enqueue(nqi);
                 */
            }

            case (wq_stop) :{
                sending = false;
                break;
            }
            case (wq_start): {
                sending = true;
                break;
            }
            case (wq_none): {
                /*
                 * Nothing in the work queue so do some work, such as reading sensors.
                 */
                if (sending) {
                    buff.add_data(&count, sizeof(count));
                    count++;
                    //Check if it's been a while since we sent some data:
                    size_t bw = buff.bytes_written.load();
                    if (bw > last_send + 100 * sizeof(count)) {
                        //Send some data:
                        nqi.type = nq_send;
                        nqi.nbytes = 100 * sizeof(count);
                        nqi.total_bytes = bw;

                        qn.enqueue(nqi);
                        //std::cout << "Sending 200 bytes" << std::endl;
                        last_send = bw;
                        //TODO this carries a risk of missing some data. Fine on single worker thread, but bad.
                        usleep(1000);
                    }
                }
                //TODO update send data periodically instead of this way.

            }
        }
    }

}

#define CIRC_SIZE 1 << 12

network_queue_item null_nqi = {nq_none}; //An item for null args to
work_queue_item null_wqi = {wq_none}; //An object with the non-matching type to do nothing.

circular_buffer buff (CIRC_SIZE);

int main(int argc, char **argv) {
    int port = 1234;

    safe_queue<network_queue_item> qn (null_nqi);
    safe_queue<work_queue_item> qw (null_wqi);

    network_queue_item initial = {};
    initial.type = nq_recv;

    qn.enqueue(initial);

    echo_worker ew(qn, qw, buff);
    network_worker nw(qn, qw, port, buff);

    nw.start();
    ew.start();
    nw.wait();
    ew.wait();
}