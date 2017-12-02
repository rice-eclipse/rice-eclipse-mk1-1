//
// Created by rjcunningham on 12/1/17.
//

#include <iostream>
#include "unistd.h"
#include "main_worker.hpp"
#include "../util/timestamps.hpp"
#include "pins.hpp"

#define COUNT_PER_SEND 2000

network_queue_item null_nqi = {nq_none}; //An item for null args to
work_queue_item null_wqi = {wq_none}; //An object with the non-matching type to do nothing.

adc_reading adcd = {};

static int ti_count = 0;
static timed_item ti_list[MAX_TIMED_LIST_LEN] = {};

static void add_timed_item(timed_item &ti) {
    int i;
    for (i = 0; i < MAX_TIMED_LIST_LEN; i++) {
        if (ti_list[i].a == wq_none) {
            ti_list[i] = ti;
            ti_count++;
            return;
        }
    }
}

static void check_ti_list(timestamp_t t, safe_queue<work_queue_item> &qw) {
    int i, ti_seen = 0;
    work_queue_item wqi;
    for (i = 0; i < MAX_TIMED_LIST_LEN && ti_seen < ti_count; i++) {
        if (ti_list[i].a != wq_none) {
            ti_seen++;
            if (ti_list[i].enabled && t > ti_list[i].scheduled && t - ti_list[i].scheduled > ti_list[i].delay) {
                // Add this to the list of items to process:
                wqi.action = wq_timed;
                wqi.extra_datap = (void *) &ti_list[i];
                qw.enqueue(wqi);
            }
        }
    }
    return;
}

static void enable_ti_item(timed_item *ti, timestamp_t now) {
    ti->scheduled = now;
    ti->enabled = true;
}

static void disable_ti_item(timed_item *ti) {
    ti->enabled = false;
}

static timed_item lc1_ti = {
        0,
        LC1_T,
        NULL,
        {
                RPI_BPLUS_GPIO_J8_03, // TODO replace with something else. Fuck.
                0, //dummy pad
                true, //use single channel (always true right now)
                0 //the channel number
        },
        lc1,
        true,
};


void init_timed_items() {
    timestamp_t now = get_time();
    size_t buff_size = 2 << 18;


    ti_list[0] = lc1_ti;
    lc1_ti.b = new circular_buffer(buff_size);
    lc1_ti.scheduled = now;
}

void main_worker::worker_method() {
    network_queue_item nqi;
    work_queue_item wqi;
    char c;
    bool sending = false;
    size_t last_send = 0;
    uint16_t count = 0;


    init_timed_items();

    while (1) {
        //std::cout << "Backworker entering loop:\n";
        wqi = qw.poll();
        //std::cout << "Backworker got item:\n";
        timestamp_t now = get_time();
        switch (wqi.action) {
            case (wq_process): {
                c = wqi.data[0];

                std::cout << "Processing request on worker: " << c << std::endl;

                switch (c) {
                    case '0': {
                        wqi.action = wq_start;
                        qw.enqueue(wqi);
                        break;
                    }
                    case '1': {
                        wqi.action = wq_stop;
                        qw.enqueue(wqi);
                        break;
                    }
                    case unset_valve: {
                        std::cout << "Writing main valve off" << std::endl;
                        bcm2835_gpio_write(MAIN_VALVE, LOW);
                        break;
                    }
                    case set_valve: {
                        std::cout << "Writing main valve on" << std::endl;
                        bcm2835_gpio_write(MAIN_VALVE, HIGH);
                        break;
                    }
                    case unset_ignition: {
                        std::cout << "Writing ignition off" << std::endl;
                        bcm2835_gpio_write(IGN_START, LOW);
                        break;
                    }
                    case set_ignition: {
                        std::cout << "Writing ignition on" << std::endl;
                        bcm2835_gpio_write(IGN_START, HIGH);
                        break;
                    }
                    default: {
                        wqi.action = wq_none;
                        qw.enqueue(wqi);
                        break;
                    }
                }
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
            case (wq_timed): {
                // Get the timed item that added this:
                timed_item *ti = (timed_item *) wqi.extra_datap;

                ti->scheduled = now;
                if (ti->b != NULL) {

                } else {
                    // Handle the case of using ignition stuff.
                    if (ti->a == ign2) {
                        disable_ti_item(ti);
                        // Enable the second igntion thing:
                        // TODO
                    }
                    if (ti->a == ign3) {
                        // Disable ignition 3.
                        disable_ti_item(ti);
                    }
                }
                break;
            }
            case (wq_none): {
                check_ti_list(now, qw);
                break;
            }

            default: {
                std::cerr << "Work queue item not hanlded." << std::endl;
                break;
            }

        }
    }

}
