from tcutils.ping import ping
import redis


class NetworkError(BaseException):
    pass


class RedisDB:
    DEFAULTPORT = 6379

    def __init__(self, host, port=DEFAULTPORT):
        if not ping(host):
            raise NetworkError("Host {} is unreachable.".format(host))
        self._host = host
        self._port = port
        self._connection = None
        self._connect()

    def _connect(self):
        if self._connection:
            Warning(ConnectionError("Already connected to DB, ignoring _connect call."))
        else:
            self._connection = redis.Connection(self._host, self._port)

    def _disconnect(self):
        if not self._connection:
            raise ConnectionError("No active connection.")
        self._connection.disconnect()
        self._connection = None

    def execute(self, command):
        if not self._connection:
            self._connect()
        self._connection.send_command(command)
        return self._connection.read_response()


def test():
    db = RedisDB("127.0.0.1")
    print(db.execute("ECHO 'Hello'"))


if __name__ == '__main__':
    pass
