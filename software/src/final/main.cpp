//
// Created by rjcunningham on 11/29/17.
//

#include <cstdio>
#include <iostream>
#include <bcm2835.h>
#include "initialization.hpp"
#include "../adc/lib/adc_block.hpp"
#include "pins.hpp"
#include "../server/queue_items.hpp"
#include "../server/safe_queue.hpp"
#include "main_worker.hpp"
#include "main_network_worker.hpp"

circular_buffer buff(CIRC_SIZE);

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

    if (!bcm2835_init()) {
        std::cerr << "bcm2835_init failed. Are you running as root??\n" << std::endl;
        return 1;
    }

    if (initialize_pins() != 0) {
        std::cerr << "Could not initialize hardware." << std::endl;
        return 1;
    };

    if (initialize_spi() != 0) {
        std::cerr << "Could not initialize SPI." << std::endl;
        return 1;
    };

    adc_block adcs = adc_block(3);
    adcs.register_pin(0, ADC_0_CS);
    adcs.register_pin(1, ADC_1_CS);
    adcs.register_pin(2, ADC_2_CS);

    // Now we create our network and hardware workers:
    safe_queue<network_queue_item> qn (null_nqi);
    safe_queue<work_queue_item> qw (null_wqi);

    network_queue_item initial = {};
    initial.type = nq_recv;

    qn.enqueue(initial);

    main_worker cw(qn, qw, buff, adcs);
    main_network_worker nw(qn, qw, port, buff);

    nw.start();
    cw.start();
    nw.wait();
    cw.wait();
}