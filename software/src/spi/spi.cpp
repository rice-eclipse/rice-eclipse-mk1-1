/**
 * Modified from bcm2835 example SPI code.
 * Original Author: Mike McCauley
 * Modifier: RJ Cunningham
 * 
 * Simple example that reads data from channel zero of MCP3208 ADC
 */
#include <bcm2835.h>
#include <stdio.h>
#include <byteswap.h>
int main(int argc, char **argv)
{
    // If you all this, it will not actually access the GPIO
// Use for testing
//        bcm2835_set_debug(1);
    char writeb[4] = {(char) 0x06,(char) 0xc0, 0, 0}; //Write to pick the first channel.
    char readb[4] = {0,0,0, 0};
    uint16_t out_value = 0;

    if (!bcm2835_init())
    {
      printf("bcm2835_init failed. Are you running as root??\n");
      return 1;
    }
    if (!bcm2835_spi_begin())
    {
      printf("bcm2835_spi_begin failed. Are you running as root??\n");
      return 1;
    }
    bcm2835_spi_chipSelect(BCM2835_SPI_CS0);                      // The default
    bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);      // The default
    bcm2835_spi_setDataMode(BCM2835_SPI_MODE3);                   // The MCP... uses this.
    //bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_256); // Just under 1MHz
    bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_1024); // Seems like 1Mhz is too fast to charge internal cap.
    bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, LOW);      // the default
    while (1) { 
        // Send 3 bytes to the slave and simultaneously read bytes back from the slave
        // If you tie MISO to MOSI, you should read back what was sent
        bcm2835_spi_transfernb(writeb, readb, 3);
        //Copy the middle two bytes into out_value:
        readb[1] &= 0x0F;
        readb[2] &= 0xFF;
        out_value = *((uint16_t *)(readb + 1));
        //Zero the upper crap.
        //out_value = out_value & (0x0FFF);
        // Next swap endianness because it's backwards for us.
        out_value = __bswap_16(out_value);
        printf("Sent to SPI: 0x%01X. Read back from SPI: 0x%03X.\n", 0x0c, out_value);
    }
    bcm2835_spi_end();
    bcm2835_close();
    return 0;
}

