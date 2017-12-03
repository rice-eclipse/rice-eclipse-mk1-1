# A file used to store information related to the information sent by the server on the PI:

# Information on the values of headers sent:
import socket
import sys

class ServerInfo:
    """
    A class that contains all the configuration info, like if we're connected to a pi or not.
    Used to track manually unpacking structs and other dumb stuff.
    """
    def __init__(self):
        self.on_pi = True
        self.info = ServerInfo.PiInfo
        pass

    def int_from_net_bytes(self, b):
        """
        Converts a bytearray received from the network to an integer type 2 or 4 bytes.
        :param b: A bytearray
        :return: A 2 or 4 byte int.
        """
        if len(b) == 4:
            i = int.from_bytes(b, self.info.byteorder)
            # TODO need to check if my computer and raspberry pi differ in endianness.
            # Really hacky if this is the fix.
            # print("4 byte int:" + str(i))
            return i  # socket.ntohl(i)
        if len(b) == 2:
            i = int.from_bytes(b, self.info.byteorder)
            # print("2 byte int:" + str(i))
            return i  # socket.ntohs(i)

        if (len(b) == 8):
            i = int.from_bytes(b, self.info.byteorder)
            # NO 8 byte byteswap, which is an annoying problem.
            # Not sure if we need it at all however.
            # print("8 byte int:" + str(i))
            return i

        return None

    ACK_VALUE = bytes([1])
    PAYLOAD = bytes([2])
    TEXT = bytes([3])
    UNSET_VALVE = bytes([4])
    SET_VALVE = bytes([5])
    SET_IGNITION = bytes([6])
    UNSET_IGNITION = bytes([7])
    LC_MAINS = bytes([9]),
    LC1S = bytes([10]),
    LC2S = bytes([11]),
    LC3S = bytes([12]),
    PT_FEEDS = bytes([13]),
    PT_INJES = bytes([14]),
    PT_COMBS = bytes([15]),
    TC1S = bytes([16]),
    TC2S = bytes([17]),
    TC3S = bytes([18])


    class PiInfo:
        byteorder='little'

        header_type_bytes = 1
        header_nbytes_offset = 4
        header_nbytes_info = 4
        header_end_pad_bytes = 0
        header_size = 8

        payload_data_bytes = 2
        payload_padding_bytes = 6
        payload_time_bytes = 8
        payload_time_offset = 8
        payload_bytes = 16

    class OtherInfo:
        byteorder='little'

        header_type_bytes = 1
        header_nbytes_offset = 8
        header_nbytes_info = 4
        header_end_pad_bytes = 4
        header_size = 16

        payload_data_bytes = 2
        payload_padding_bytes = 6
        payload_time_bytes = 8
        payload_time_offset = 8
        payload_bytes = 16

    def payload_from_bytes(self, b):
        assert len(b) == self.info.payload_bytes

        data = b[:self.info.payload_data_bytes]
        data = self.int_from_net_bytes(data)

        t = b[self.info.payload_time_offset:self.info.payload_time_offset + self.info.payload_time_bytes]
        t = self.int_from_net_bytes(t)

        return data, t

    def read_payload(self, b, nbytes, out_queue):
        assert nbytes % self.info.payload_bytes == 0

        bcount = 0
        while bcount < nbytes:
            d, t = self.payload_from_bytes(b[bcount: bcount + self.info.payload_bytes])
            bcount += self.info.payload_bytes
            # TODO handle multiple out queues
            out_queue.put((d, t))

    def decode_header(self, b):
        htype = b[:self.info.header_type_bytes]

        nbytesb = b[self.info.header_nbytes_offset: self.info.header_nbytes_offset + self.info.header_nbytes_info]

        return htype, self.int_from_net_bytes(nbytesb)
