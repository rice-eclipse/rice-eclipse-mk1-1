import socket
import threading
from queue import Queue

# A class used to handle all the networking:
import sys

from logger import LogLevel, Logger
from server_info import *


# MAJOR TODO move this networker to processing requests on its own thread and then let it attempt reconnection.
class Networker:
    class NWThread(threading.Thread):
        def __init__(self, threadID, name, counter, nw):

            assert(isinstance(nw, Networker))

            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.counter = counter
            self.nw = nw

        def run(self):
            while True:
                # Ensure we are connected:
                self.nw.conn_event.wait()

                # Try to receive a message:
                t,nb,m = self.nw.read_message()
                if (t is not None):
                    self.nw.out_queue.put((t, nb, m))

    @staticmethod
    def make_socket():
        sock = socket.socket()
        # 10ms timeout, with the intent of giving just a bit of time if receiving.
        sock.settimeout(0.01)

        return sock

    def __init__(self, queue=None, loglevel = LogLevel.DEBUG):
        self.sock = self.make_socket()
        self.addr = None
        self.port = None
        self.connected = False
        self.trying_connect = False
        #TODO for now we only have the data receiving on a separate thread because that was straightforward:
        self.out_queue = queue if queue is not None else Queue()
        self.conn_event = threading.Event()

        self.thr = Networker.NWThread(1, 'NWThread', 1, self)
        self.thr.start()
        self.logger = Logger(name='networker', level=loglevel, outfile='networker.log')

        self.logger.info("Initialized")

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
                self.logger.error("Connect timed out.")
            except OSError as e:
                self.logger.error("Connection failed. OSError:" + e.strerror)
                self.trying_connect = False
            except:
                self.logger.error("Connect: Unexpected error:" + str(sys.exc_info()[0]))
                self.trying_connect = False
            else:
                self.logger.error("Successfully connected.")
                self.trying_connect = False
                self.connected = True
                self.conn_event.set()

    def disconnect(self):
        """
        Disconnects and resets and connection information.
        :return: None
        """
        if not self.connected:
            return

        self.conn_event.clear()
        self.connected = False
        self.logger.warn("Socket disconnecting:")
        self.sock.close()

        # Recreate the socket so that we aren't screwed.
        self.sock = self.make_socket()

    def send(self, message):
        """
        Sends a bytearray.
        :param message:
        :return: True if no exceptions were thrown:
        """
        # TODO logging levels?
        self.logger.debug("Sending message:")
        # TODO proper error handling?
        try:
            self.sock.send(message)
        except socket.timeout:
            self.logger.error("Socket timed out while sending")
            self.disconnect()
        except OSError as e:
            self.logger.error("Connection failed. OSError:" + e.strerror)
            self.disconnect()
        except:
            self.logger.error("Unexpected error:" + str(sys.exc_info()[0]))
            self.disconnect()
        else:
            self.logger.info("Message sent")
            return True

        return False

    def read_message(self):
        """
        Reads a full message including header from the PI server.
        :return: The header type, the number of bytes, the message.
        """
        if not self.connected:
            self.logger.error("Trying to read while not connected")
            raise Exception("Not connected. Cannot read.")

        htype, nbytes = self.read_header()

        if nbytes is None or nbytes == 0:
            message = None
        else:
            message = self._recv(nbytes)

        if (message is not None):
            self.logger.debug("Received Full Message: Type:" + str(htype) +
                           " Nbytes:" + str(nbytes) + " message" + str(message))

        return htype, nbytes, message

    def read_header(self):
        """
        Reads a data header from PI server.
        :return: The header type, The number of bytes
        """
        htype = self._recv(header_type_bytes)
        if (len(htype) == 0):
            return None, None


        dummy_pad = self._recv(header_pad_bytes)

        nbytes = self._recv(header_nbytes_info)

        dummy_pad = self._recv(header_end_pad_bytes)

        self.logger.debugv("Bytes form of nbytes:" + str(nbytes))
        nbytes = int_from_net_bytes(nbytes)
        if (nbytes is not None and nbytes > 1):
            nbytes = 1

        self.logger.debugv("Received message header: Type:" + str(htype) + " Nbytes:" + str(nbytes))

        return htype, nbytes

    def _recv(self, nbytes):
        """
        Receives a message of length nbytes from the socket. Will retry until all bytes have been received.
        :param nbytes: The number of bytes to receive.
        :return: The bytes.
        """
        #print("Attempting to read " + str(nbytes) + " bytes")
        outb = bytes([])
        bcount = 0
        try:
            while nbytes > 0:
                b = self.sock.recv(nbytes)
                nbytes -= len(b)
                bcount += len(b)
                outb += b
        except socket.timeout:
            if bcount > 0:
                #TODO fix this.
                self.logger.error("Socket timed out during partial read. Major problem.")
        except OSError as e:
            self.logger.error("Read failed. OSError:" + e.strerror)
        except:
            self.logger.error("Read: Unexpected error:" + str(sys.exc_info()[0]))
        else:
            return outb

        return bytes([])
