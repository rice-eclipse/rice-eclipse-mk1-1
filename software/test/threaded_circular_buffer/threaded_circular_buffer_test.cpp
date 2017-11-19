//
// Created by rjcunningham on 9/7/17.
//
#include <iostream>
#include "../../src/server/safe_queue.hpp"
#include "../../src/server/queue_items.hpp"
#include "../../src/util/circular_buffer.hpp"
#include "../../src/util/listener.hpp"
#include "../../src/util/timestamps.hpp"
#include <thread>
#include <poll.h>
#include <cmath>

#define DEBUG_ADC_TEST

#define SAMPLES_TO_SEND 100

struct adc_reading {
    uint16_t value;
    timestamp_t t;
};

network_queue_item null_nqi = {nq_none}; //An item for null args to

work_queue_item null_wqi = {wq_none}; //An object with the non-matching type to do nothing.

/**
 * Function used by the network thread.
 */
void network_thread(safe_queue<network_queue_item> &qn, safe_queue<work_queue_item> &qw, int port);

/**
 * Function used for the worker thread.
 */
void worker_thread(safe_queue<network_queue_item> &qn, safe_queue<work_queue_item> &qw);

#define CIRC_SIZE 1 << 14
circular_buffer buff (CIRC_SIZE);

int main(int argc, char **argv) {

    set_base_time();

    int port = 1234; //TODO set this from inputs.

    safe_queue<network_queue_item> qn (null_nqi);
    safe_queue<work_queue_item> qw (null_wqi);

    network_queue_item initial = {};
    initial.type = nq_recv;

    qn.enqueue(initial);

    //Initialize the threads.
    std::thread t_worker(&worker_thread, std::ref(qn), std::ref(qw));
    std::thread t_network(&network_thread, std::ref(qn), std::ref(qw), port);

    //Block until both threads finish execution.
    t_worker.join();
    t_network.join();
}

void worker_thread(safe_queue<network_queue_item> &qn, safe_queue<work_queue_item> &qw) {
    network_queue_item nqi;
    work_queue_item wqi;
    char c;
    bool sending = false;
    size_t last_send = 0;
    adc_reading adc_value = {};

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

                    adc_value.t = get_time();
                    //Read the ADC (num = 0, use dual channel, use channel 0 (pin 0=+, pin 1 =-))
                    adc_value.value = count;
                    //adc_value.value = sin(count);
                    count++;
                    usleep(1000); // Pretend like we slept for a while.

                    #ifdef DEBUG_ADC_TEST
                        fprintf(stderr, "ADC reading: %u. Time: %llu \n", adc_value.value, (long long) adc_value.t);
                    #endif
                    buff.add_data(&adc_value, sizeof(adc_value));
                    //Check if it's been a while since we sent some data:
                    size_t bw = buff.bytes_written.load();
                    if (bw > last_send + SAMPLES_TO_SEND * sizeof(adc_value)) {
                        //Send some data:
                        nqi.type = nq_send;
                        nqi.nbytes = SAMPLES_TO_SEND * sizeof(adc_value);
                        nqi.total_bytes = bw;

                        qn.enqueue(nqi);
                        //std::cout << "Sending 200 bytes" << std::endl;
                        last_send = bw;
                        //TODO this carries a risk of missing some data. Fine on single worker thread, but bad.
                        //usleep(100);
                    }
                }
                //TODO update send data periodically instead of this way.

            }
        }
    }

}

void network_thread(safe_queue<network_queue_item> &qn, safe_queue<work_queue_item> &qw, int port) {
    ssize_t read_result;
    char c;
    network_queue_item nqi;
    work_queue_item wqi;


    int connfd = wait_for_connection(port, NULL);
    if (connfd < 0)
        std::cerr << "Could not open connection fd." << std::endl;

    /*
 * Stuff used to poll the socket:
 */
    pollfd pf;
    pf.fd = connfd;
    pf.events = POLLIN | POLLOUT;


    while (1) {
        //std::cout << "Networker entering loop:\n";
        nqi = qn.poll();
        //std::cout << "Networker got item:\n";
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
            }
        }
    }
}

