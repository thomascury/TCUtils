import platform
import asyncio
import os
import sys
import shlex


def usage():
    print('''Usage: %s host1 [host2 [host3...]]
Ping 1 to N hosts.
''' % os.path.basename(sys.argv[0]))


@asyncio.coroutine
def ping(host: str) -> bool:
    """
    Returns True if host responds to a ping request
    :param host: string
    :return: boolean
    """
    # Ping parameters
    ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    command = "ping " + ping_str + " " + host
    args = shlex.split(command)

    process = yield from asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE)
    # Read one line of output

    yield from process.wait()
    return host, process.returncode == 0


def multiping(host_list):
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    tasks = [ping(host) for host in host_list]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    print(results)

    loop.close()


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    multiping(sys.argv[1:])

if __name__ == '__main__':
    main()
