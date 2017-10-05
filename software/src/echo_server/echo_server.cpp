//
// Created by rjcunningham on 9/7/17.
//
#include <iostream>
#include "listener.hpp"
int main(int argc, char **argv) {
    int port = 1234; //TODO set this from inputs.
    ssize_t read_result;
    char c;

    int connfd = wait_for_connection(port, NULL);
    if (connfd < 0)
        std::cerr << "Could not open connection fd." << std::endl;

    while (1) {
        read_result = read(connfd, &c, 1);
        //TODO figure out how this works when connection is closed. Catch connection closed.
        std::cout << c;
    }
}