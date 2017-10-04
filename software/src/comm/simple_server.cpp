//
// Created by rjcunningham on 9/24/17.
//

#include <cstdio>
#include <iostream>
#include "../echo_server/listener.hpp"
#include "Ipi_server.hpp"

class simple_server : public Ipi_server {
    public:
        simple_server(int port) {
            this->port = port;
            this->connfd = wait_for_connection(this->port, NULL);
            if (connfd < 0)
                std::cerr << "Could not open connection fd." << std::endl;
        }

        ~simple_server() {
            close(connfd);
        }

        int send_data() {
            return 0;
        }

        int recv_data() {
            char c;
            read(connfd, &c, 1);
            std::cout << c;
        }

        int connfd;

        int port;
};

int main(int argc, char **argv) {
    int port = 1234; //TODO set this from inputs.
    simple_server *ss = new simple_server(port);
    while (true) {
        ss->recv_data();
    }
}