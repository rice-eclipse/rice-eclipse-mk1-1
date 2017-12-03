# A file used to store information related to the information sent by the server on the PI:

# Information on the values of headers sent:
import csv
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
    NORM_IGNITE = bytes([8])
    LC_MAINS = bytes([9])
    LC1S = bytes([10])
    LC2S = bytes([11])
    LC3S = bytes([12])
    PT_FEEDS = bytes([13])
    PT_INJES = bytes([14])
    PT_COMBS = bytes([15])
    TC1S = bytes([16])
    TC2S = bytes([17])
    TC3S = bytes([18])

    filenames = {
        LC1S : 'logs/LC1.log',
        LC_MAINS : 'logs/LC_MAIN.log',
        LC2S : 'logs/LC2.log',
        LC3S : 'logs/LC3.log',
        PT_FEEDS : 'logs/PT_FEED.log',
        PT_COMBS : 'logs/PT_COMB.log',
        PT_INJES : 'logs/PT_INJE.log',
        TC1S : 'logs/TC1.log',
        TC2S : 'logs/TC2.log',
        TC3S : 'logs/TC3.log'
    }

    averages = {
        LC1S: 0,
        LC_MAINS: 0,
        LC2S: 0,
        LC3S: 0,
        PT_FEEDS: 0,
        PT_COMBS: 0,
        PT_INJES: 0,
        TC1S: 0,
        TC2S: 0,
        TC3S: 0
    }

    calibrations = {
        LC1S: (1, 0),
        LC_MAINS: (0.1371, -66.115),
        LC2S: (1, 0),
        LC3S: (1, 0),
        PT_FEEDS: (1, 0),
        PT_COMBS: (1, 0),
        PT_INJES: (1, 0),
        TC1S: (1, 0),
        TC2S: (1, 0),
        TC3S: (1, 0)
    }

    print(TC1S)
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

    def read_payload(self, b, nbytes, out_queue, mtype = None):
        assert nbytes % self.info.payload_bytes == 0

        #print(mtype, mtype in ServerInfo.filenames.keys())
        #print(ServerInfo.filenames.keys())

        if (mtype != None and mtype in ServerInfo.filenames.keys()):
            save_file = open(ServerInfo.filenames[mtype], 'a')
            writer = csv.writer(save_file, delimiter=" ")
            #print("Starting logger for message")
        else:
            save_file = None
            writer = None

        bcount = 0
        while bcount < nbytes:
            d, t = self.payload_from_bytes(b[bcount: bcount + self.info.payload_bytes])
            bcount += self.info.payload_bytes
            # TODO handle multiple out queues

            if (mtype in ServerInfo.averages.keys()):
                ServerInfo.averages[mtype] = 0.5 * ServerInfo.averages[mtype] + 0.5 * d

            if (mtype in ServerInfo.calibrations.keys()):
                calib = ServerInfo.calibrations[mtype]
                cal = d * calib[0] + calib[1]
            else:
                cal = 0

            if (save_file != None):
                writer.writerow([str(t), str(d), str(cal)])
            if (out_queue is not None):
                out_queue.put((cal, t))

        if (save_file is not None):
            save_file.close()

    def decode_header(self, b):
        htype = b[:self.info.header_type_bytes]

        #print(htype)
        nbytesb = b[self.info.header_nbytes_offset: self.info.header_nbytes_offset + self.info.header_nbytes_info]

        return htype, self.int_from_net_bytes(nbytesb)
