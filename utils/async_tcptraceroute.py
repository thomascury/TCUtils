import os
import re
import sys
import struct
import socket
import time
import asyncio


def usage():
    print('''Usage: %s host port
Tries to connect to host at TCP port with increasing TTL (Time to live).
If /etc/services exists (on most Unix systems), you can give the protocol
name for the port. Example 'ssh' instead of 22.
''' % os.path.basename(sys.argv[0]))


def average(iterable):
    return sum(map(lambda x: x or 0, iterable))/len(iterable)  # Lambda is here to fix None value


@asyncio.coroutine
def get_socket(ttl, timeout=.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
    sock.settimeout(timeout)
    return sock


@asyncio.coroutine
def tcping(host, port, ttl):
    sock = yield from get_socket(ttl)
    start = None
    stop = None
    peer = None
    establishment_time = None
    try:
        start = time.time()
        sock.connect((host, int(port)))
        stop = time.time()
        peer, _ = sock.getpeername()
    except (socket.error, socket.timeout) as err:
        establishment_time = err
    except KeyboardInterrupt:
        establishment_time = ConnectionAbortedError("KeyboardInterrupt")
    finally:
        if start and stop:
            establishment_time = stop - start
    return ttl, peer, establishment_time


def traceroute(host, port):
    loop = asyncio.get_event_loop()

    tasks = [tcping(host, port, ttl) for ttl in range(30)]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    print(results)

    loop.close()


def main():
    if not len(sys.argv) == 3:
        usage()
        sys.exit(1)
    host, port = sys.argv[1:]
    traceroute(host, port)

if __name__ == '__main__':
    main()
