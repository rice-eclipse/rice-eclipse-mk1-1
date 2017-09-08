//
// Created by rjcunningham on 9/7/17.
//

#include "listener.hpp"

/*
 * Requires:
 *   "port" should be a valid port number on the machine in use.
 *
 * Effects:
 *   Opens a socket to listen on "port". Returns the file descriptor of the
 *   socket or -1 on error.
 */
int
open_listen(int port)
{
    int listenfd, optval=1;
    struct sockaddr_in serveraddr;

    /* Set "listenfd" to a newly created stream socket */
    if ((listenfd = socket(PF_INET, SOCK_STREAM, 0)) == -1) {
        return (-1);
    }

    //Not needed.
    /* Eliminates "Address already in use" error from bind. */
    if (setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR,
                   (const void *)&optval , sizeof(int)) < 0)
        return (-1);

    /*
    * Set the IP address of serveraddr to be the special ANY IP address
    * and set port to be the input port.  Be careful to ensure that the
    * IP address and port are in network byte order.
    */
    bzero((char *) &serveraddr, sizeof(serveraddr));
    serveraddr.sin_family = AF_INET;
    serveraddr.sin_port = htons((uint16_t) port);
    //Raspberry Pi will only have one interface, just use ANY.
    serveraddr.sin_addr.s_addr = htonl(INADDR_ANY);

    /* Use bind to set the address of "listenfd" to be serveraddr */
    if (bind(listenfd, (struct sockaddr *) &serveraddr,
             sizeof(struct sockaddr)) == -1) {
        return (-1);
    }

    /* Use listen to make the socket ready to accept connection requests */
    if (listen(listenfd, LISTEN_MAX) == -1) {
        return (-1);

    }

    return listenfd;
}

int
wait_for_connection(int port, sockaddr *sa) {
    socklen_t clientlen;
    int listenfd, connfd;
    /* Acquire a port, and make sure we got it successfully. */
    listenfd = open_listen(port);
    if (listenfd < 0) {
        fprintf(stderr, "Failed to open listener on %d\n", port);
        exit(1);
    }

    clientlen = sizeof(struct sockaddr_in);

    /*
     * Use accept to set the connection file descriptor of the
     * request
     */
    connfd = accept(listenfd, sa,
                    &clientlen);


    return connfd;

}