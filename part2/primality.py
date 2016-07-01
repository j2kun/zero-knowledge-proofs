import random


def decompose(n):
    exponentOfTwo = 0

    while n % 2 == 0:
        n = n // 2  # using / turns large numbers into floats
        exponentOfTwo += 1

    return exponentOfTwo, n


def isWitness(possibleWitness, p, exponent, remainder):
    if pow(possibleWitness, remainder, p) == 1:
        return False

    if any(pow(possibleWitness, 2**i * remainder, p) == p - 1 for i in range(exponent)):
        return False

    return True


def probablyPrime(p, accuracy=100):
    if p == 2 or p == 3:
        return True
    if p < 2 or p % 2 == 0:
        return False

    exponent, remainder = decompose(p - 1)

    for _ in range(accuracy):
        possibleWitness = random.randint(2, p - 2)
        if isWitness(possibleWitness, p, exponent, remainder):
            return False

    return True


if __name__ == "__main__":
    n = 1

    while not probablyPrime(n, accuracy=100):
        n = random.getrandbits(512)

    print("{} is prime".format(n))
