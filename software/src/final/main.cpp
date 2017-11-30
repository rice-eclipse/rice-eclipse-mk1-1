//
// Created by rjcunningham on 11/29/17.
//

#include <cstdio>
#include <iostream>
#include "initialization.hpp"

/**
 * A target that runs the final code and does everything.
 *
 * Usage final <Port>
 *
 * Requires the following arguments:
 *   <Port>
 *      Sets the port on which the program listens for connections.
 *
 * @return 0 unless an error occurs.
 */
int main(int argc, char **argv) {
    // Validate the arguments. TODO use a real argparse library
    int port;
    if (argc != 2) {
        std::cerr << "Incorrect number of arguments. Usage final <port>" << std::endl;
    }

    port = atoi(argv[1]);

    if (port <= 0) {
        std::cerr << "Port must be larger than zero." << std::endl;
    }

    if (initialize_pins() != 0) {
        std::cerr << "Could not initialize hardware." << std::endl;
    };
}