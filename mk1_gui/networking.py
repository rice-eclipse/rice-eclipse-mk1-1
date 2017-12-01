import socket
import threading
from queue import Queue

# A class used to handle all the networking:
import sys

from server_info import *


class Networker:
    def __init__(self):
        self.sock = socket.socket()
        self.addr = None
        self.port = None
        self.connected = False
        self.trying_connect = False

    def connect(self, addr=None, port=None):
        """
        Connects to a given address and port or just tries to reconnect (if args are none or same).
        :param addr: The address to connect
        :param port: The port to connect to.
        :return: None
        """
        # First check if the port or address have changed and if so we should disconnect.
        if addr is not None and self.addr != addr:
            self.disconnect()
            self.addr = addr


        if port is not None and self.port != port:
            self.disconnect()
            self.port = port

        if self.connected:
            return

        self.trying_connect = True
        while self.trying_connect:
            try:
                self.sock.connect((self.addr, int(self.port)))
            except socket.timeout:
                print("Connect timed out.")
            except:
                print("Unexpected error:", sys.exc_info()[0])
                self.trying_connect = False
            else:
                print("Successfully connected.")
                self.trying_connect = False
                self.connected = True

    def disconnect(self):
        """
        Disconnects and resets and connection information.
        :return: None
        """
        self.connected = False
        self.sock.close()

    def send(self, message):
        """
        Sends a bytearray.
        :param message:
        :return:
        """
        self.sock.send(message)

    def read_message(self):
        """
        Reads a full message including header from the PI server.
        :return: The header type, the number of bytes, the message.
        """
        if not self.connected:
            raise Exception("Not connected. Cannot read.")

        htype, nbytes = self.read_header()

        message = self._recv(nbytes)

        return htype, nbytes, message

    def read_header(self):
        """
        Reads a data header from PI server.
        :return: The header type, The number of bytes
        """
        htype = self._recv(header_type_bytes)

        dummy_pad = self._recv(header_pad_bytes)

        nbytes = self._recv(header_nbytes_info)
        nbytes = int_from_net_bytes(nbytes)

        return htype, nbytes

    def _recv(self, nbytes):
        """
        Receives a message of length nbytes from the socket. Will retry until all bytes have been received.
        :param nbytes: The number of bytes to receive.
        :return: The bytes.
        """
        outb = bytes([])
        bcount = 0
        while nbytes > 0:
            b = self.sock.recv(nbytes)
            nbytes -= len(b)
            outb += b

        return outb
