//
// Created by rjcunningham on 9/7/17.
//

#ifndef SOFTWARE_LISTENER_HPP
#define SOFTWARE_LISTENER_HPP

#include "strings.h"
#include "unistd.h"
#include <netinet/in.h>
#include <cstdio>
#include <cstdlib>

#define DEBUG_LISTENER

#define LISTEN_MAX 1

/*
 * Requires:
 *  "port" is a valid port number on the machine in use.
 *  "sa" is either an allocated sockaddr_in port or NULL.
 *
 * Effects:
 *  Listens on the port specified and blocks until a connection is recieved
 *  and then returns the corresponding fildes for the connection.
 *  TODO not sure what is being done with "sa"
 */
int wait_for_connection(int port, sockaddr *sa);

/*
 * Requires:
 *   "port" should be a valid port number on the machine in use.
 *
 * Effects:
 *   Opens a socket to listen on "port". Returns the file descriptor of the
 *   socket or -1 on error.
 */
int open_listen(int port);

#endif //SOFTWARE_LISTENER_HPP
