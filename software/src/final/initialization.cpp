//
// Created by rjcunningham on 11/29/17.
//

#include <bcm2835.h>
#include <iostream>
#include "initialization.hpp"
#include "pins.hpp"

void initialize_pins() {
    // Set all the ADC chip selects to HIGH so that they don't interfere.
    bcm2835_gpio_fsel(ADC_0_CS, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_write(ADC_0_CS, HIGH);

    bcm2835_gpio_fsel(ADC_1_CS, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_write(ADC_1_CS, HIGH);

    bcm2835_gpio_fsel(ADC_2_CS, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_write(ADC_2_CS, HIGH);

    // Set all the ignition and relay outputs to LOW so that they don't trigger.
    bcm2835_gpio_fsel(MAIN_VALVE, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_write(MAIN_VALVE, LOW);

    bcm2835_gpio_fsel(VALVE_2, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_write(VALVE_2, LOW);

    bcm2835_gpio_fsel(VALVE_3, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_write(VALVE_3, LOW);

    bcm2835_gpio_fsel(IGN_START, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_write(IGN_START, LOW);

    // Setup all the SPI stuff:

    return;
}

int initialize_spi() {

    if (!bcm2835_spi_begin()) {
        std::cerr << "bcm2835_spi_begin failed. Are you running as root?" << std::endl;
        return 1;
    }

    bcm2835_spi_chipSelect(BCM2835_SPI_CS_NONE);                      // Default, leave it for now.
    bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);      // Necessary for MCP
    bcm2835_spi_setDataMode(BCM2835_SPI_MODE3);                   // The MCP... uses this.

    //bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_256); // Just under 1MHz
    bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_1024); // Seems like 1Mhz is too fast to charge internal cap.
    bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, LOW);      // Active low.
    bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS1, LOW);      // Active low.

    // Create the ADC block and

    return 0;
}
