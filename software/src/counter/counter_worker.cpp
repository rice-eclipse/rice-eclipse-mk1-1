//
// Created by rjcunningham on 11/18/17.
//

#include "unistd.h"
#include <iostream>
#include "counter_worker.hpp"
#include "network_counter_worker.hpp"

struct dummy_reading {
    uint16_t count;
    uint64_t t;
} reading;

#define COUNT_PER_SEND 100

void counter_worker::worker_method() {
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
                    reading.count = count;
                    reading.t = count;
                    buff.add_data(&reading, sizeof(reading));
                    count++;

                    if (usleep(10000) != 0) {
                        perror("sleep");
                    }

                    //Check if it's been a while since we sent some data:
                    size_t bw = buff.bytes_written.load();
                    if (bw > last_send + COUNT_PER_SEND * sizeof(reading)) {
                        //Send some data:
                        nqi.type = nq_send;
                        nqi.nbytes = bw - last_send;
                        nqi.total_bytes = last_send;
                        nqi.buff = &buff;

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

#define CIRC_SIZE 1 << 16

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

    counter_worker cw(qn, qw, buff);
    network_counter_worker nw(qn, qw, port);

    nw.start();
    cw.start();
    nw.wait();
    cw.wait();
}