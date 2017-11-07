#!/usr/bin/env python3
# -*- coding: utf-8 -*-


""" sniffer.py
    ...Packet sniffer
    Original by: Silver Moon (m00n.silv3r@gmail.com)
                 http://www.binarytides.com/python-packet-sniffer-code-linux/

    This one has been modified to run on Python 3 also.
    -Christopher Welborn 08-27-2014
"""

from docopt import docopt
import os
import sys
import socket
import sys
from struct import *

NAME = 'Sniffer'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr}
    Usage:
        {script} [-h | -v]
        {script} -r

    Options:
        -h,--help     : Show this help message.
        -r,--raw      : Show raw bytes repr() instead of trying to decode.
        -v,--version  : Show version.
""".format(script=SCRIPT, versionstr=VERSIONSTR)

RAWBYTES = False


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd """
    global RAWBYTES
    RAWBYTES = argd['--raw']

    # create a AF_PACKET type raw socket (thats basically packet level)
    # define ETH_P_ALL    0x0003          /* Every packet (be careful!!!) */
    try:
        s = socket.socket(
            socket.AF_PACKET,
            socket.SOCK_RAW,
            socket.ntohs(0x0003))
    except socket.error as exmsg:
        print('Socket could not be created.')
        print('    Error Code : {}'.format(getattr(exmsg, 'errno', '?')))
        print('       Message : {}'.format(exmsg))
        sys.exit()

    try:
        ret = packet_loop(s)
    except KeyboardInterrupt:
        print('\nUser cancelled.\n')
        ret = 1
    return ret


def packet_loop(s):
    # receive a packet
    while True:
        packet = s.recvfrom(65565)

        # packet string from tuple
        packet = packet[0]

        # parse ethernet header
        eth_length = 14

        eth_header = packet[:eth_length]
        eth = unpack('!6s6sH', eth_header)
        eth_protocol = socket.ntohs(eth[2])
        addrinfo = [
            'Destination MAC: {}'.format(eth_addr(packet[0:6])),
            'Source MAC: {}'.format(eth_addr(packet[6:12])),
            'Protocol: {}'.format(eth_protocol)
        ]
        print(' '.join(addrinfo))

        # Parse IP packets, IP Protocol number = 8
        if eth_protocol == 8:
            # Parse IP header
            # take first 20 characters for the ip header
            ip_header = packet[eth_length:20 + eth_length]

            # now unpack them :)
            iph = unpack('!BBHHHBBH4s4s', ip_header)

            version_ihl = iph[0]
            version = version_ihl >> 4
            ihl = version_ihl & 0xF

            iph_length = ihl * 4

            ttl = iph[5]
            protocol = iph[6]
            s_addr = socket.inet_ntoa(iph[8])
            d_addr = socket.inet_ntoa(iph[9])

            headerinfo = [
                'Version: {}'.format(version),
                'IP Header Length: {}'.format(ihl),
                'TTL: {}'.format(ttl),
                'Protocol: {}'.format(protocol),
                'Source Addr: {}'.format(s_addr),
                'Desr.Addr: {}'.format(d_addr)]
            print(' '.join(headerinfo))

            # TCP protocol
            if protocol == 6:
                t = iph_length + eth_length
                tcp_header = packet[t:t + 20]

                # now unpack them :)
                tcph = unpack('!HHLLBBHHH', tcp_header)

                source_port = tcph[0]
                dest_port = tcph[1]
                sequence = tcph[2]
                acknowledgement = tcph[3]
                doff_reserved = tcph[4]
                tcph_length = doff_reserved >> 4

                tcpinfo = [
                    'Source Port: {}'.format(source_port),
                    'Dest. Port: {}'.format(dest_port),
                    'Sequence Num: {}'.format(sequence),
                    'Acknowledgement: {}'.format(acknowledgement),
                    'TCP Header Len.: {}'.format(tcph_length),
                ]
                print(' '.join(tcpinfo))

                h_size = eth_length + iph_length + tcph_length * 4
                data_size = len(packet) - h_size

                # get data from the packet
                data = packet[h_size:]

                print('Data: {}'.format(data_decode(data)))

            # ICMP Packets
            elif protocol == 1:
                u = iph_length + eth_length
                icmph_length = 4
                icmp_header = packet[u:u + 4]

                # now unpack them :)
                icmph = unpack('!BBH', icmp_header)

                icmp_type = icmph[0]
                code = icmph[1]
                checksum = icmph[2]

                icmpinfo = [
                    'Type: {}'.format(icmp_type),
                    'Code: {}'.format(code),
                    'Checksum: {}'.format(checksum)
                ]
                print(' '.join(icmpinfo))

                h_size = eth_length + iph_length + icmph_length
                data_size = len(packet) - h_size

                # get data from the packet
                data = packet[h_size:]

                print('Data : {}'.format(data_decode(data)))

            # UDP packets
            elif protocol == 17:
                u = iph_length + eth_length
                udph_length = 8
                udp_header = packet[u:u + 8]

                # now unpack them :)
                udph = unpack('!HHHH', udp_header)

                source_port = udph[0]
                dest_port = udph[1]
                length = udph[2]
                checksum = udph[3]

                udpinfo = [
                    'Source Port: {}'.format(source_port),
                    'Dest. Port: {}'.format(dest_port),
                    'Length: {}'.format(length),
                    'Checksum: {}'.format(checksum)
                ]
                print(udpinfo)

                h_size = eth_length + iph_length + udph_length
                data_size = len(packet) - h_size

                # get data from the packet
                data = packet[h_size:]

                print('Data: {}'.format(data_decode(data)))

            # some other IP packet like IGMP
            else:
                print('Protocol other than TCP/UDP/ICMP')

            print('')
    return 0


def data_decode(b):
    if RAWBYTES:
        return repr(b)
    if sys.version_info.major == 2:
        return b
    return b.decode('ascii', errors='replace')


def eth_addr(a):
    """ Convert a string of 6 characters of ethernet address into a
        dash separated hex string
    """
    pieces = (a[i] for i in range(6))
    return '{:2x}:{:2x}:{:2x}:{:2x}:{:2x}:{:2x}'.format(*pieces)


def eth_addr2(a):
    """ Same as eth_addr, for Python 2 """
    pieces = tuple(ord(a[i]) for i in range(6))
    return '%.2x:%.2x:%.2x:%.2x:%.2x:%.2x' % pieces


if __name__ == '__main__':
    if sys.version_info.major == 2:
        eth_addr = eth_addr2

    mainret = main(docopt(USAGESTR, version=VERSIONSTR))
    sys.exit(mainret)
