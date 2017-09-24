//
// Created by rjcunningham on 9/24/17.
//

#ifndef SOFTWARE_IPI_SERVER_HPP
#define SOFTWARE_IPI_SERVER_HPP

/**
 * An interface for a server that communicates from the pi to the base station. Allows for sending data. Also has
 * a function that reads from the base station. Definitely not intelligently written for longterm so this interface
 * will need some tweaking as we progress to a more complex system. It should be sufficient for what I really want
 * to do over the next two weeks and more development will still be possible from there.
 */
class Ipi_server {
    public:
        /**
         * Creates the server and initializes any socket file-descriptors if need be.
         */
        //virtual Ipi_server() = 0;

        /**
         * Sends any data that needs to be sent since the last invocation.
         * @return Returns 0 if no error.
         */
        virtual int send_data() = 0;

        /**
         * Reads from the base station and responds appropriately.
         * @return Returns 0 if no error.
         */
        virtual int recv_data() = 0;

        /**
         * A virtual destructor that is called when it is necessary to clear any object associated with this server.
         * Most likely not necessary for our use case as the server should be alive the entire time the pi code runs.
         */
        virtual ~Ipi_server(){};
};


#endif //SOFTWARE_IPI_SERVER_HPP
