#!/usr/bin/env python
# (c) December 2007 Thomas Guettler http://www.thomas-guettler.de
# tcptraceroute.py
# This script is in the public domain

import os
import re
import sys
import struct
import socket
import time


def usage():
    print('''Usage: %s host port
Tries to connect to host at TCP port with increasing TTL (Time to live).
If /etc/services exists (on most Unix systems), you can give the protocol
name for the port. Example 'ssh' instead of 22.
''' % os.path.basename(sys.argv[0]))


def average(iterable):
    return sum(map(lambda x: x or 0, iterable))/len(iterable)  # Lambda is here to fix None value


class Connection:
    def __init__(self, host, port, ttl, timeout=2.):
        self.host = host
        self.port = port
        self.ttl = ttl
        self.timeout = timeout
        self.socket = None
        self.establishment_time = None
        self.connection_error = None
        self.connected = False
        self.peer = None

    @staticmethod
    def get_socket(ttl, timeout=2.):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
        sock.settimeout(timeout)
        return sock

    def connect(self):
        start = None
        stop = None
        self.socket = self.get_socket(self.ttl, self.timeout)
        try:
            start = time.time()
            self.socket.connect((self.host, self.port))
            stop = time.time()
            self.peer, _ = self.socket.getpeername()
        except (socket.error, socket.timeout) as err:
            return err
        except KeyboardInterrupt:
            return ConnectionAbortedError("KeyboardInterrupt")
        finally:
            self.connected = True
            if start and stop:
                self.establishment_time = stop - start
        return None

    def disconnect(self):
        self.socket.close()
        self.connected = False
        return True

    def time(self, cached=True):
        if not (cached and self.establishment_time):
            self.connection_error = self.connect()
            self.disconnect()
        return self.establishment_time, self.connection_error


class TCPing:
    def __init__(self, host, port):
        self.host = host
        port_int = None
        try:
            port_int = int(port)
        except ValueError:
            if not os.path.exists('/etc/services'):
                print('port needs to be an integer if /etc/services does not exist.')
                sys.exit(1)
            fd = open('/etc/services')
            for line in fd:
                port_int = None
                match = re.match(r'^%s\s+(\d+)/tcp.*$' % port, line)
                if match:
                    port_int = int(match.group(1))
                    break
            if not port_int:
                print('port %s not in /etc/services' % port)
                sys.exit(1)
        self.port = port_int

    def run(self, tries=3, timeout=2.):
        hosts = []
        for ttl in range(1, 30):
            con = Connection(self.host, self.port, ttl, timeout)
            timings = []
            error = None
            for i in range(tries):
                timing, error = con.time(cached=False)
                timings.append(timing)
            if len(hosts) > 0 and con.peer and con.peer == hosts[-1] and con.peer == self.host:
                break
            hosts.append(con.peer)
            timing = str(int((average(timings) or timeout)*1000))+"ms"
            if error:
                timing = timing + " ({})".format(error)
            print("TTL={} {} {}:{}".format(ttl, timing, con.peer or "Unknown host", self.port))


def main():
    if not len(sys.argv) == 3:
        usage()
        sys.exit(1)
    host, port = sys.argv[1:]
    tcping = TCPing(host, port)
    tcping.run(timeout=.5)

if __name__ == '__main__':
    main()
