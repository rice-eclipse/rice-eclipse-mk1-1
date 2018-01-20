//
// Created by rjcunningham on 12/1/17.
//

#ifndef SOFTWARE_PINS_HPP
#define SOFTWARE_PINS_HPP

#include <bcm2835.h>
extern RPiGPIOPin ADC_0_CS;
extern RPiGPIOPin ADC_1_CS;
extern RPiGPIOPin ADC_2_CS;

extern RPiGPIOPin MAIN_VALVE;
extern RPiGPIOPin VALVE_2;
extern RPiGPIOPin VALVE_3;
extern RPiGPIOPin IGN_START;

extern RPiGPIOPin LC_ADC;
extern RPiGPIOPin PT_ADC;
extern RPiGPIOPin TC_ADC;
#endif //SOFTWARE_PINS_HPP
