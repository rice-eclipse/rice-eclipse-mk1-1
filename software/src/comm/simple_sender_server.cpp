//
// Created by rjcunningham on 9/24/17.
//

#include <cstdio>
#include <iostream>
#include "../echo_server/listener.hpp"
#include "Ipi_server.hpp"

class simple_sender_server : public Ipi_server {
    public:
        simple_sender_server(int port) {
            this->port = port;
            this->connfd = wait_for_connection(this->port, NULL);
            if (connfd < 0)
                std::cerr << "Could not open connection fd." << std::endl;

            count = 0;
        }

        ~simple_sender_server() {
            close(connfd);
        }

        int send_data() {
            write(connfd, &count, 2);
            //printf("count:%d\n", count);
            count++;
        }

        int recv_data() {
            return 0;
        }

        uint16_t count;

        int connfd;

        int port;
};

int main(int argc, char **argv) {
    int port = 1234; //TODO set this from inputs.
    simple_sender_server *ss = new simple_sender_server(port);
    while (true) {
        ss->send_data();
    }
}