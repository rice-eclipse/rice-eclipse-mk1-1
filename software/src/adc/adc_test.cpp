//
// Created by Thomas Yuan on 9/28/2017.
//

#include "adc_block.hpp"
#include "adc_block.cpp"
#include <iostream>

int main() {
    std::cout << "Testing ADC!" << std::endl;

    if (!bcm2835_init()) {
        printf("bcm2835_init failed. Are you running as root??\n");
        return 1;
    }
    if (!bcm2835_spi_begin()) {
        printf("bcm2835_spi_begin failed. Are you running as root??\n");
        return 1;
    }

    adc_block *block = new adc_block(1);
    uint16_t data;

    while(1) {
        data = block->read_item(0, 1, 0x0c);
        printf("Sent to SPI: 0x%01X. Read back from SPI: 0x%03X.\n", 0x0c, data);
    }
}