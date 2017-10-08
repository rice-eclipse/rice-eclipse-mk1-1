//
// Created by rjcunningham on 10/8/17.
//
#include "../catch.hpp"
#include "../../src/util/circular_buffer.hpp"
#include <sys/mman.h>
#include <fcntl.h>

#define TEMP_FILE "tmp.txt"

TEST_CASE("Circular buffer gets values sequentially", "[cb]") {
    size_t cb_size = 64;
    circular_buffer cb(cb_size);
    cb.zero();
    REQUIRE(cb.bytes_written == 0);
    REQUIRE(cb.nbytes == cb_size);

    SECTION("Write ascending bytes in increments of ones") {
        uint8_t i;
        int j;
        for (i = 0; i < cb_size;i++) {
            cb.add_data(&i, 1);
            //Now verify the buffer's contents from 0 to i
            for (j = 0; j <= i; j++) {
                REQUIRE(cb.data[j] == j);
            }
        }
    }

    SECTION("Write ascending bytes in increments of fours") {
        uint8_t b[4];
        uint8_t i;
        int j;
        for (i = 0; i *4 + 3 < cb_size;i++) {
            b[0] = (uint8_t) (4*i);
            b[1] = (uint8_t) (4*i + 1);
            b[2] = (uint8_t) (4*i + 2);
            b[3] = (uint8_t) (4*i + 3);
            cb.add_data(b, 4);
            //Now verify the buffer's contents from 0 to i
            for (j = 0; j <= 4 * i + 3; j++) {
                REQUIRE(cb.data[j] == j);
            }
        }
    }

    SECTION("Write some overflowing bytes") {
        char b[cb_size];
        cb.add_data(b, cb_size - 1);
        b[0] = 10;
        b[1] = 11;
        cb.add_data(b, 2);
        REQUIRE(cb.data[0] == b[1]);
        REQUIRE(cb.data[cb.nbytes - 1] == b[0]);
    }
}

TEST_CASE("Circular buffer can write correctly", "[cb]") {
    size_t cb_size = 64;
    circular_buffer cb(cb_size);
    cb.zero();
    int fdbuf = open(TEMP_FILE, O_RDWR | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);

    REQUIRE(fdbuf >= 0);

    //MMAP a file at temp.txt as write to mess with a fd in the program memory:
    size_t out_buf_size = cb_size * 4;
    char * out_buf = (char *) mmap(nullptr, out_buf_size, PROT_READ | PROT_WRITE, MAP_PRIVATE, fdbuf, 0);

    SECTION("Write ascending values in ones and output in ones") {
        uint8_t i;
        int j;
        for (i = 0; i < cb_size;i++) {
            cb.add_data(&i, 1);
            //Now verify the buffer's contents from 0 to i
            for (j = 0; j <= i; j++) {
                REQUIRE(cb.data[j] == j);
            }
        }

        //Now do the outputs
        for (i = 0; i < cb_size;i++) {
            cb.write_data(fdbuf, 1, i);
            for (j = 0; j <= i; j++) {
                REQUIRE(out_buf[j] == j); //Now check the mmapped output.
            }
        }
    }

    SECTION("Write ascending values in fours and output in fours") {
        uint8_t b[4];
        uint8_t i;
        int j;
        for (i = 0; i *4 + 3 < cb_size;i++) {
            b[0] = (uint8_t) (4*i);
            b[1] = (uint8_t) (4*i + 1);
            b[2] = (uint8_t) (4*i + 2);
            b[3] = (uint8_t) (4*i + 3);
            cb.add_data(b, 4);
            //Now verify the buffer's contents from 0 to i
            for (j = 0; j <= 4 * i + 3; j++) {
                REQUIRE(cb.data[j] == j);
            }
        }

        //Now output the values:
        for (i = 0; i *4 + 3 < cb_size;i++) {
            cb.write_data(fdbuf,4, (size_t) i * 4);
            //Now verify the buffer's contents from 0 to i
            for (j = 0; j <= 4 * i + 3; j++) {
                REQUIRE(out_buf[j] == j);
            }
        }


    }

    SECTION("Write some overflowing data") {
        char b[cb_size];
        cb.add_data(b, cb_size - 1);
        b[0] = 10;
        b[1] = 11;
        cb.add_data(b, 2);
        REQUIRE(cb.data[0] == b[1]);
        REQUIRE(cb.data[cb.nbytes - 1] == b[0]);

        //Now tell cb to write two bytes starting from the second to last:
        cb.write_data(fdbuf, 2, cb.nbytes - 1);
        REQUIRE(out_buf[0] == b[0]);
        REQUIRE(out_buf[1] == b[1]);

        //Now tell cb to write two bytes starting from the second to last:
        //Test writing the same bytes again a big offset.
        cb.write_data(fdbuf, 2, cb.nbytes - 1 + 100 * cb.nbytes);
        REQUIRE(out_buf[2] == b[0]);
        REQUIRE(out_buf[3] == b[1]);
    }

    REQUIRE(munmap(out_buf, out_buf_size) == 0);
}