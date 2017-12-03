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
    int port, result;
    if (argc != 2) {
        std::cerr << "Incorrect number of arguments. Usage final <port>" << std::endl;
        return 1;
    }

    port = atoi(argv[1]);

    if (port <= 0) {
        std::cerr << "Port must be larger than zero." << std::endl;
        return 1;
    }


    if (!bcm2835_init()) {
        std::cerr << "bcm2835_init failed. Are you running as root??\n" << std::endl;
        return 1;
    }

    initialize_pins();

    if (initialize_spi() != 0) {
        std::cerr << "Could not initialize SPI." << std::endl;
        return 1;
    };

    result = atexit(initialize_pins);
    if (result != 0) {
        std::cerr << "Could not register exit function." << std::endl;
        return 1;
    }

    adc_block adcs = adc_block(3);
    adcs.register_pin(0, ADC_0_CS);
    adcs.register_pin(1, ADC_1_CS);
    adcs.register_pin(2, ADC_2_CS);
/*
    adc_info fuck = {RPI_V2_GPIO_P1_26, 1, true, 0};
    while (true) {
        adcs.read_item(fuck);
    }
*/
    // Set the base time so that we have no risk of overflow.
    set_base_time();



    // Now we create our network and hardware workers:
    safe_queue<network_queue_item> qn (null_nqi);
    safe_queue<work_queue_item> qw (null_wqi);

    network_queue_item initial = {};
    initial.type = nq_recv;

    qn.enqueue(initial);


    main_network_worker nw(qn, qw, port, buff);
    main_worker cw(qn, qw, buff, adcs, &nw);

    nw.start();
    cw.start();
    nw.wait();
    cw.wait();
}
