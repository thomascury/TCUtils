def recursive(n):
    if n <= 0:
        return 0
    if n == 1 or n == 2:
        return 1
    return recursive(n - 1) + recursive(n - 2)


def loop(n):
    a, b = 1, 1
    for i in range(n-1):
        a, b = b, a+b
    return a
