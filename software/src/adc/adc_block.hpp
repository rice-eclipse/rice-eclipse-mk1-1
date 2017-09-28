//
// Created by rjcunningham on 9/20/17.
//

#ifndef SOFTWARE_ADC_BLOCK_HPP
#define SOFTWARE_ADC_BLOCK_HPP

#include <cstdint>
#include <bcm2835.h>

/**
 * A simple structure that holds information on which ADC to read from.
 * Used to pair a sensor with an ADC and a channel
 */
struct adc_info {
    uint8_t adc_num;         //ADC to use
    int pad             :4; //Pad an extra four bits.
    bool single_channel :1; //The :1 means use one bit for this.
    uint8_t channel     :3; //The three bits to pick channel.
};

/**
 * A class that abstracts away all the ADCs on the system.
 */
class adc_block {

    /*
     * TODO Need to figure out a way to register pins associated with chip select.
     * One solution is to create a header pins.hpp in a folder somewhere and use that?
     * Then this will only work if we link against pins.hpp so only one possible options for pins, which is
     * bad for breadboarding. The other option is to create a shared object that contains the pin information
     * instead. That way I think it'll be provided by some externs and depending on which .so you link against then
     * the same code will work. It's a bit convoluted. I think at least for the ADC it's probably fine to just use a
     * pins.hpp option.
     */
private:
    RPiGPIOPin *adcs;
    uint8_t num_adcs;


    //TODO pass error code in upper 4 bits of the return value of return item?
public :
    /**
     * Creates this with a set number of adcs to use.
     * @param num_adcs The number of adcs to use.
     */
    adc_block(uint8_t num_adcs);

    /**
     * The destructor for the adc_block. Frees memory used to store pin assignments.
     */
    ~adc_block();

    /**
     * Read a single item from the specified registered item given by idx.
     * @param idx The channel to read from.
     * @return The result of reading that channel on that adc.
     */
    uint16_t read_item(adc_info idx);

    /**
     * Reads a single item from the specified adc with parameters given here.
     * @param adc_num Which ADC to select and read from.
     * @param single_channel
     * @param channel
     * @return
     */
    uint16_t read_item(uint8_t adc_num, bool single_channel, uint8_t channel);


    /**
     * TODO should this be exposed at all? Probably not worth implementing this in any meaningful way.
     * Set the number of ADCS that will be controlled by this block.
     * @param num The number of adcs to control.
     */
    //void set_number_adcs(uint8_t num);

    /**
     * Registers a pin with this adc_block.
     * @param adc_num The adc number to associate with the pin.
     * @param pin_num The pin to use as chip select for this adc.
     */
    void register_pin(uint8_t adc_num, RPiGPIOPin pin_num);
};

#endif //SOFTWARE_ADC_BLOCK_HPP
