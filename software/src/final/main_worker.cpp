//
// Created by rjcunningham on 12/1/17.
//

#include "unistd.h"
#include "main_worker.hpp"
#include "../util/timestamps.hpp"
#include "pins.hpp"

#define COUNT_PER_SEND 2000

network_queue_item null_nqi = {nq_none}; //An item for null args to
work_queue_item null_wqi = {wq_none}; //An object with the non-matching type to do nothing.

adc_reading adcd = {};

void main_worker::worker_method() {
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
                c = wqi.data[0];

                switch (c) {
                    case '0': {
                        wqi.action = wq_start;
                    }
                    case '1': {
                        wqi.action = wq_stop;
                    }
                    case unset_valve: {
                        bcm2835_gpio_write(MAIN_VALVE, LOW);
                    }
                    case set_valve: {
                        bcm2835_gpio_write(MAIN_VALVE, HIGH);
                    }
                    case unset_ignition: {
                        bcm2835_gpio_write(MAIN_VALVE, LOW);
                    }
                    case set_ignition: {
                        bcm2835_gpio_write(MAIN_VALVE, HIGH);
                    }
                    default: {
                        wqi.action = wq_none;
                    }
                }

                qw.enqueue(wqi);
                break;
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
                    //adcd.count = count;
                    adcd.dat = adcs.read_item(0, true, 0);
                    adcd.t = get_time();
                    buff.add_data(&adcd, sizeof(adc_reading));

                    //adcd.count = count;
                    adcd.dat = adcs.read_item(0, true, 1);
                    adcd.t = get_time();
                    buff.add_data(&adcd, sizeof(adc_reading));

                    adcd.dat = adcs.read_item(1, true, 0);
                    adcd.t = get_time();
                    buff.add_data(&adcd, sizeof(adc_reading));

                    adcd.dat = adcs.read_item(2, true, 0);
                    adcd.t = get_time();
                    buff.add_data(&adcd, sizeof(adc_reading));

                    if (usleep(1000) != 0) {
                        perror("sleep");
                    }

                    //Check if it's been a while since we sent some data:
                    size_t bw = buff.bytes_written.load();
                    if (bw > last_send + COUNT_PER_SEND * sizeof(adc_reading)) {
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