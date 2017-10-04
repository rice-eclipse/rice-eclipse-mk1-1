//
// Created by rjcunningham on 9/7/17.
//
#include <iostream>
#include "listener.hpp"
#include "../server/safe_queue.hpp"
#include "../server/queue_items.hpp"
#include <thread>

/**
 * Function used by the network thread.
 */
void network_thread(safe_queue<network_queue_item> &qn, safe_queue<work_queue_item> &qw, int port);

/**
 * Function used for the worker thread.
 */
void worker_thread(safe_queue<network_queue_item> &qn, safe_queue<work_queue_item> &qw);

int main(int argc, char **argv) {
    int port = 1234; //TODO set this from inputs.

    safe_queue<network_queue_item> qn;
    safe_queue<work_queue_item> qw;

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

    while (1) {
        //std::cout << "Backworker entering loop:\n";
        wqi = qw.dequeue();
        //std::cout << "Backworker got item:\n";
        switch (wqi.action) {
            case (wq_process): {
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

    while (1) {
        //std::cout << "Networker entering loop:\n";
        nqi = qn.dequeue();
        //std::cout << "Networker got item:\n";
        switch (nqi.type) {
            case (nq_recv): {
                read_result = read(connfd, &c, 1);
                wqi.action = wq_process;
                wqi.data = (uint8_t) c;
                qw.enqueue(wqi);
                break;
            }
            case (nq_send): {
                c = nqi.data;
                //std::cout << "sending\n";
                if (write(connfd, &c, 1) != 1) {
                    std::cerr << "Connection Closed" << std::endl;
                    exit(0);
                }
                nqi.type = nq_recv;
                qn.enqueue(nqi); //Start the read again.
                break;

            }
        }
    }
}

