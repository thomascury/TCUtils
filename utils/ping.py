def ping(host: str) -> bool:
    """
    Returns True if host responds to a ping request
    :param host: string
    :return: boolean
    """
    import subprocess
    import platform

    # Ping parameters
    ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"

    # Ping
    status, result = subprocess.getstatusoutput("ping " + ping_str + " " + host)
    return status == 0
