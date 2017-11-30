//
// Created by rjcunningham on 11/29/17.
//

#include "main_network_worker.hpp"
bool main_network_worker::process_nqi(network_queue_item &nqi) {
    switch (nqi.type) {
        case (nq_send_ack): {
            send_header h = {ack, 0};

        }
        default: {
            return network_worker::process_nqi(nqi);
        }
    }
}