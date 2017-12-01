# A file used to store information related to the information sent by the server on the PI:

# Information on the values of headers sent:
import socket
import sys

ACK_VALUE = bytes([1])
PAYLOAD = bytes([2])

#############################################################################

# Information on the padding of c structs that are sent raw by the PI server:

header_type_bytes = 1
header_pad_bytes = 3  # Not sure?
header_nbytes_info = 4 # Verify this?

header_struct = (header_type_bytes,
                 header_pad_bytes,
                 header_nbytes_info)

#############################################################################


def int_from_net_bytes(b):
    """
    Converts a bytearray received from the network to an integer type 2 or 4 bytes.
    :param b: A bytearray
    :return: A 2 or 4 byte int.
    """
    if len(b) == 4:
        i = int.from_bytes(b, byteorder=sys.byteorder)
        return socket.ntohl(i)
    if len(b) == 2:
        i = int.from_bytes(b, byteorder=sys.byteorder)
        return socket.ntohs(i)
