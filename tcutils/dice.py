from os import urandom
import sys


def roll(i):
    return tuple(r % 6 + 1 for r in urandom(i))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        print(roll(int(sys.argv[1])))
    else:
        print(roll(1))
