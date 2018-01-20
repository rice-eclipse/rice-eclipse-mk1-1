//
// Created by rjcunningham on 11/29/17.
//

#ifndef SOFTWARE_INITIALIZATION_HPP
#define SOFTWARE_INITIALIZATION_HPP

/**
 * Sets all pins and to the default state.
 * @return 0 unless an error occurs.
 */
void initialize_pins();

/**
 * Initializes all the SPI stuff and ADC stuff.
 */
int initialize_spi();

#endif //SOFTWARE_INITIALIZATION_HPP
