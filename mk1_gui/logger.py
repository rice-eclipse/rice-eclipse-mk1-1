"""
Author: Kevin Lin, kevinlin@rice.edu
Modified version of Logger used by Skynet Senior Design team at Rice University.
"""

import time


class LogLevel:
    """
    Mapping of log level enums to names.
    """
    DEBUGV = {'name': 'DEBUGV', 'value' : 4}
    DEBUG = {'name': 'DEBUG', 'value': 3}
    INFO = {'name': 'INFO', 'value': 2}
    WARN = {'name': 'WARN', 'value': 1}
    ERROR = {'name': 'ERROR', 'value': 0}


class Logger:
    def __init__(self, name, level=LogLevel.DEBUG, outfile=None):
        """
        Initializes a logger.

        :param name: Name to attach to every log entry generated with this logger.
        :param level: The log level at which to supress messages.
        """
        self.name = name
        self.level = level

        if outfile != None:
            self.fout = open(outfile, mode='a')
        else:
            self.fout = None

    def debugv(self, message):
        """
        Log a debug message.

        :param message: Message to log.
        """
        return self._print_log(LogLevel.DEBUGV, message)

    def debug(self, message):
        """
        Log a debug message.

        :param message: Message to log.
        """
        return self._print_log(LogLevel.DEBUG, message)

    def info(self, message):
        """
        Log an info message.

        :param message: Message to log.
        """
        return self._print_log(LogLevel.INFO, message)

    def warn(self, message):
        """
        Log a warning message.

        :param message: Message to log.
        """
        return self._print_log(LogLevel.WARN, message)

    def error(self, message):
        """
        Log an error message.

        :param message: Message to log.
        """
        return self._print_log(LogLevel.ERROR, message)

    def _print_log(self, level, message):
        """
        Print a log entry to standard output, with the timestamp, log level, and context name
        automatically prefixed.

        :param level: Target log level.
        :param message: Message to log.
        """
        # Don't print if we are supressing the message:
        if self.level['value'] < level['value']:
            return


        hms = time.strftime('%H:%M:%S')
        self._print_stdout(
            '[{hms}] [{name}] [{level}] {message}'.format(
                hms=hms,
                name=self.name,
                level=level['name'],
                message=message,
            )
        )

    def _print_stdout(self, line):
        """
        Print a line to standard output.

        :param line: Line to print.
        """
        print(line)
        if self.fout is not None:
            self.fout.write(line + '\n')
            self.fout.flush()
