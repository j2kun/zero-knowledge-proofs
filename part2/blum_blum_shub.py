from primality import probablyPrime
import random


def goodPrime(p):
    return p % 4 == 3 and probablyPrime(p, accuracy=100)


def findGoodPrime(numBits=512):
    candidate = 1

    while not goodPrime(candidate):
        candidate = random.getrandbits(numBits)

    return candidate


def makeModulus(numBits=512):
    return findGoodPrime(numBits) * findGoodPrime(numBits)


def parity(n):
    return sum(int(x) for x in bin(n)[2:]) % 2


def blum_blum_shub(modulusLength=512):
    modulus = makeModulus(numBits=modulusLength)

    def f(inputInt):
        return pow(inputInt, 2, modulus)

    return f


if __name__ == "__main__":
    owp = blum_blum_shub()
    print(owp(70203203))
    print(owp(12389))
