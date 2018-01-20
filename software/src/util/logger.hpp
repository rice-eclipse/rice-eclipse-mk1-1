//
// Created by rjcunningham on 1/8/18.
//

#ifndef SOFTWARE_LOGGER_HPP
#define SOFTWARE_LOGGER_HPP

#include <string>
#include <fstream>
#include "timestamps.hpp"

typedef std::string string;
//TODO better way to do this?

enum LOG_LEVEL {
    LOG_DEBUG_VERBOSE = 0,
    LOG_DEBUG = 1,
    LOG_WARNING = 2,
    LOG_ERROR = 3,

};

class logger {
    public:
        string logfile;
        string name;
        LOG_LEVEL level;

        /**
         * Creates a logger object with a specified name and output logfile.
         * @param logfile A relative path (from the program's working directory) to create logs.
         * @param name The name of the logger to print.
         * @param level The loglevel to use for this logger.
         */
        logger(string &logfile, string &name, LOG_LEVEL level);

        /**
         * Logs a message to the logfile.
         * @param message the logfile.
         * @param level The loglevel to which to log.
         */
        void log_message(string &message, LOG_LEVEL level);

        /**
         * Logs a message to the logfile.
         * @param message the logfile.
         * @param level The loglevel to which to log.
         * @param t The time to use for the message.
         */
        void log_message(string &message, LOG_LEVEL level,timestamp_t t);

    private:
        std::ofstream of;

};


#endif //SOFTWARE_LOGGER_HPP
