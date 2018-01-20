//
// Created by rjcunningham on 1/8/18.
//

#include "logger.hpp"

logger::logger(string &logfile, string &name, LOG_LEVEL level)
        : logfile (logfile)
        , name (name)
        , level (level)
{
    // TODO should be be opening this here?
    //of.open(logfile);
}

void logger::log_message(string &message, LOG_LEVEL level) {
    log_message(message, level, get_time());
}

void logger::log_message(string &message, LOG_LEVEL level,timestamp_t t) {
    if (level < logger::level) {
        return;
    }
    string s = std::to_string(t);

    of.open(name);
    of.write(s.data(), s.length());
    of.write(message.data(), message.length());
    of.put('\n');
    of.close();
}

